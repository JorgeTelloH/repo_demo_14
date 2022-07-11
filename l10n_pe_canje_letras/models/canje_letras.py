# -*- coding: utf-8 -*-
from . import helper
from odoo import api, exceptions, fields, models, _
from datetime import timedelta, datetime
from odoo.tools import float_is_zero, float_compare

from odoo.exceptions import UserError, ValidationError


class Letras(models.Model):
    _name = 'canje.letras'
    _description = 'Canje de Letras'


    @api.depends('state', 'letra_line_ids.amount_total')
    def _compute_residual(self):
        self.residual = 0

    @api.depends('letra_line_ids.amount_total')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_total = sum(line.amount_total for line in self.letra_line_ids)
        t_inv = sum(line.amount_canje_letra for line in self.invoice_ids)
        t_letr = sum(line.amount_total for line in self.letra_ids)
        self.total_invoice = t_inv + t_letr

    @api.model
    def _default_currency(self):
        journal = self.journal_id
        return journal.currency_id or journal.company_id.currency_id or self.env.user.company_id.currency_id

    name = fields.Char(string='Nro Canje', index=True, readonly=True, copy=False)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('send', 'Enviada'),
        ('validate', 'Aceptada'),
    ], string='Estado', index=True, readonly=True, default='draft', track_visibility='onchange', copy=False)

    company_id = fields.Many2one('res.company', string='Compañia', change_default=True,
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    residual = fields.Monetary(string='Residual', currency_field='currency_id',
                               compute='_compute_residual', store=True, help="Importe restante adeudado.")
    move_id = fields.Many2one('account.move', string='Asiento', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Socio',
                                 required=True, readonly=True, states={'draft': [('readonly', False)]})
    account_id = fields.Many2one('account.account', string='Cuenta',
                                 readonly=True, states={'draft': [('readonly', False)]},
                                 domain=[('deprecated', '=', False)], required=True,
                                 help="Cuenta de socio usado para esta factura.")
    numero = fields.Integer(default=1, string='Nro de letras', readonly=True, states={'draft': [('readonly', False)]} )
    journal_id = fields.Many2one('account.journal', string='Diario',
                                 required=True, readonly=True, states={'draft': [('readonly', False)]})
    payment_term_id = fields.Many2one('account.payment.term', string='Plazos de pago',
                                      readonly=True, required=True, states={'draft': [('readonly', False)]},
                                      help="Si usa Plazos de Pago, la fecha de vencimiento se calculará automáticamente en la generación "
                                           "del Asiento Contable. Si mantiene el Plazo de Pago y la fecha de vencimiento en blanco, significa Pago Directo. "
                                           "Los Plazos de Pago  pueden computar varias fechas de vencimiento.")
    letra_line_ids = fields.One2many('canje.letras.lineas', 'letra_id', string='Lineas de letras',
                                     readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    # period_id = fields.Many2one('date.range', string='Periodo',
    #                             required=True, readonly=True, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Moneda',
                                  required=True, readonly=True, states={'draft': [('readonly', False)]},
                                  default=_default_currency, track_visibility='always')
    total_invoice = fields.Monetary(string='Monto para el canje', currency_field='currency_id',
                                    compute='_compute_amount')
    amount_total = fields.Monetary(string='Total',
                                   store=True, readonly=True, compute='_compute_amount')
    invoice_ids = fields.One2many('canje.detalle.factura', 'letra_id', string='Lineas de Facturas',
                                  states={'draft': [('readonly', False)]}, copy=False, readonly=True, )
    letra_ids = fields.Many2many(string='Letras canje', comodel_name='canje.letras.lineas')
    date = fields.Date(string='Fecha de canje', copy=False, required=True)
    exchange = fields.Float(string='Tipo de Cambio', digits='Tipo Cambio')
    comment = fields.Text(string='Información Adicional', readonly=True, states={'draft': [('readonly', False)]})
    move_type = fields.Selection(selection=[
        ('out_invoice', 'Cliente'),
        ('in_invoice', 'Proveedor'),
    ], string='Tipo', required=True, store=True, index=True, readonly=True, tracking=True,
        default="in_invoice", change_default=True)

    _sql_constraints = [
        ('name', 'unique(name,company_id)', 'Nro Canje único por Compañia'),
    ]


    def action_enviar(self):
        for element in self:
            # lots of duplicate calls to action_invoice_open, so we remove those already open
            if element.total_invoice < 0:
                raise ValidationError(_("Monto Total tiene que ser mayor que 0 para procesar"))

            if element.total_invoice != element.amount_total:
                raise ValidationError(_("Monto de Canje y monto de Comprobantes tiene que ser igual"))

            list_currency = []
            for line in element.letra_line_ids:
                if not line.currency_id.id in list_currency:
                    list_currency.append(line.currency_id.id)

            for line in element.invoice_ids:
                if not line.currency_id.id in list_currency:
                    list_currency.append(line.currency_id.id)

            if len(list_currency) > 1:
                raise ValidationError(_("No se puede manejar dos Tipos de monedas para un Canje"))

            if self.move_type == 'out_invoice':

                for line in element.letra_line_ids:
                    if element.company_id.id:
                        number_next = self.env['ir.sequence'].next_by_code('sale.letter') or '/'
                        # number_next = element.env['ir.sequence'].with_context(force_company=element.company_id.id).next_by_code(
                        #     'sale.letter') or '/'
                    else:
                        number_next = element.env['ir.sequence'].next_by_code('sale.letter') or '/'

                    name = number_next
                    amount_text = helper.number_to_letter(str(line.amount_total), element.currency_id.name)
                    line.write({'name': name, 'state': 'open', 'amount_letters': amount_text, 'account_id': element.account_id.id})

            if self.move_type == 'in_invoice':
                for line in element.letra_line_ids:
                    if not line.name:
                        raise ValidationError(_("Agregar Numero a cada letra"))

                    amount_text = helper.number_to_letter(str(line.amount_total), element.currency_id.name)
                    line.write({'state': 'open', 'amount_letters': amount_text,
                                'account_id': element.account_id.id})

            element.write({'state': 'send'})

    def action_validar(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        if self.total_invoice < 0:
            raise ValidationError(_("Monto total tiene que ser mayor que 0 para procesar"))

        if self.total_invoice != self.amount_total:
            raise ValidationError(_("Monto de Canje y monto de Comprobantes tiene que ser igual"))

        list_currency = []
        for line in self.letra_line_ids:
            if not line.currency_id.id in list_currency:
                list_currency.append(line.currency_id.id)

        for line in self.invoice_ids:
            if not line.currency_id.id in list_currency:
                list_currency.append(line.currency_id.id)

        if len(list_currency) > 1:
            raise ValidationError(_("No se puede manejar dos Tipos de monedas para un Canje"))

        move = self.env['account.move']
        list_line_move = self.create_credit_line()

        for line in self.letra_line_ids:
            line.write({'acept': True})
            company_currency = self.company_id.currency_id.id
            if self.move_type == 'out_invoice':
                debit = self.compute_amount(line.amount_total, company_currency, self.company_id, self.date)
                credit = 0
                factor = 1
            else:
                credit = self.compute_amount(line.amount_total, company_currency, self.company_id, self.date)
                debit = 0
                factor = -1
            amount_curren = 0
            #type_document = self.journal_id.type_document.id

            obj2 = {
                'name': line.name,
                'debit': debit,
                'credit': credit,
                'date_maturity': line.date_c,
                'date': self.date,
                'account_id': self.account_id.id,
                'currency_id': self.currency_id.id,
                'amount_currency': line.amount_total*factor,
                'partner_id': self.partner_id.id,
                'letra_id': line.id,
                # 'type_document': type_document,
                # 'value_change': self.exchange,
                # 'date_issue': self.date
            }

            list_line_move.append(obj2)

        if self.currency_id != self.company_id.currency_id:
            total_credit = 0
            total_debit = 0
            for line_c in list_line_move:
                total_credit += line_c['credit']
                total_debit += line_c['debit']

            if total_debit != total_credit:
                diff = total_debit - total_credit
                list_line_move[len(list_line_move) - 1]['debit'] = list_line_move[len(list_line_move) - 1][
                                                                       'debit'] - diff

        conver_list = []
        for line_m in list_line_move:
            if round(line_m['debit'], 2) - round(line_m['credit'], 2) != 0:
                conver_list.append((0, 0, line_m))

        res = {'journal_id': self.journal_id.id,
               'date': fields.Date.today(),
               'ref': 'Canje de letras',
               'company_id': self.company_id.id,
               # 'value_change': self.exchange,
               'line_ids': conver_list}

        res['line_ids'] = conver_list
        move_id = move.with_context(default_move_type='entry').create(res)
        move_id.post()

        for line in self.invoice_ids:
            # transfer_credit_aml = move_id.line_ids.filtered(lambda r: r.account_id == (sline.account_id or self.letra_id.account_id))
            invoice = line.invoice_id
            if invoice.move_type in ("in_invoice", "in_refund"):
                name = invoice.ref
            if invoice.move_type in ("out_invoice", "out_refund"):
                name = invoice.name
            # para tipo
            transfer_credit_aml = move_id.line_ids.filtered(lambda r: r.name == (name))
            transfer_debit_aml = self.env['account.move.line'].search(
                [('move_id', '=', invoice.id), ('account_id', '=', invoice.account_id.id)])
            (transfer_credit_aml + transfer_debit_aml).reconcile()

            #self.paid(move_id, transfer_credit_aml, transfer_debit_aml, invoice)

        for line in self.letra_ids:
            transfer_credit_aml = move_id.line_ids.filtered(lambda r: r.name == (line.name))
            transfer_debit_aml = line.letra_id.move_id.line_ids.filtered(lambda r: r.name == (line.name))
            # transfer_debit_aml = self.env['account.move.line'].search([('move_id','=',line.letra_id.move_id.id),('name','=',line.name)])
            #self.paid(move_id, transfer_credit_aml, transfer_debit_aml)
            (transfer_credit_aml + transfer_debit_aml).reconcile()
            line.write({'state': 'paid'})

        for line in move_id.line_ids:
            name_l = line.name
            for letra_l in self.letra_line_ids:
                if letra_l.name == name_l:
                    letra_l.write({'move_line_id': line.id})

        if self.move_type == 'out_invoice':
            seq = self.env['ir.sequence'].next_by_code('canje.letra') or '/'
        else:
            seq = self.env['ir.sequence'].next_by_code('canje.letra.proveedor') or '/'
        return self.write({'state': 'validate', 'move_id': move_id.id, 'name': seq})


    def compute_amount(self, mount_currency, company_currency, company_id, date):
        for element in self:
            if element.currency_id.id != company_currency:
                amount = mount_currency*element.exchange
            else:
                amount = mount_currency
            return round(amount,2)

    def create_credit_line(self):
        list_line_move=[]
        for line in self.invoice_ids:
            account = line.invoice_id.account_id.id
            company_currency = self.company_id.currency_id.id
            amount = self.compute_amount(line.amount_canje_letra, company_currency, self.company_id, self.date)
            if line.invoice_id.move_type in ("in_invoice","in_refund"):
                name = line.invoice_id.ref
            if line.invoice_id.move_type in ("out_invoice","out_refund"):
                name = line.invoice_id.name
            name1 = self.env['account.move.line'].search([('move_id','=',line.invoice_id.id),('account_id','=',line.invoice_id.account_id.id)])[0]
            if line.invoice_id.currency_id.id != self.company_id.currency_id.id:
                #amount_currency = round((credit / self.company_id.currency_id._convert(1, line.invoice_id.currency_id, self.company_id, self.date or fields.Date.today())),2)*-1
                amount_currency = line.amount_canje_letra
            else:
                amount_currency = line.amount_canje_letra

            if self.move_type == 'out_invoice':
                credit = amount
                debit = 0
                factor = -1
                amount_currency = amount_currency * factor
            else:
                credit = 0
                debit = amount
                factor = 1
                amount_currency = amount_currency * factor
            obj1={
                'name':name,
                'debit':debit,
                'credit':credit,
                'account_id':account,
                'currency_id': self.currency_id.id,
                'amount_currency':amount_currency,
                'partner_id': self.partner_id.id,
                #'type_document': line.invoice_id.l10n_latam_document_type_id.id,
                #'value_change':self.exchange,
                #'invoice_id':name1.invoice_id.id,
            }
            list_line_move.append(obj1)

        for line in self.letra_ids:
            account = line.letra_id.account_id.id
            company_currency = self.company_id.currency_id.id
            amount = self.compute_amount(line.amount_total,company_currency,self.company_id,self.date)
            #type_document = self.env['sunat.table'].search([('table_type','=','tabla10'),('code','=','00')]).id
            #type_document = self.journal_id.type_document.id

            if self.move_type == 'out_invoice':
                credit = amount
                debit = 0
                factor = -1
            else:
                debit = amount
                credit= 0
                factor = 1
            obj1={
                'name':line.name,
                'debit':debit,
                'credit':credit,
                'account_id':account,
                'currency_id': self.currency_id.id,
                'amount_currency':line.amount_total*factor,
                'partner_id': self.partner_id.id,
                #'type_document': type_document,
                #'value_change':self.exchange,
                #'letra_id':line.id
            }
            list_line_move.append(obj1)


        return list_line_move

    @api.onchange('invoice_ids')
    def _onchange_invoice(self):
        for element in self:
            if element.invoice_ids:
                element.comment = element.invoice_ids[0].invoice_id.narration
            # self.currency_id = self.invoice_ids[0].invoice_id.currency_id.id
            return {}

    @api.onchange('date', 'currency_id')
    def _onchange_exchange(self):
        # exchange_rate = 0
        # si es una nota de credito de venta o compra
        if self.company_id.currency_id.id == self.currency_id.id:
            self.exchange = 1
        else:
            # exchange_rate = self.currency_id.with_context(date=self.date).compute(
            #     1, self.company_id.currency_id, round=False)
            exchange_rate = self.currency_id._convert(1, self.company_id.currency_id, self.company_id, fields.Date.today())

            self.exchange = exchange_rate

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if not self.partner_id.id:
            return {}
        rec_account = self.partner_id.property_account_receivable_id
        pay_account = self.partner_id.property_account_payable_id
        if self.move_type == 'out_invoice':
            self.account_id = rec_account
        else:
            self.account_id = pay_account
        return {}

    @api.onchange('invoice_ids', 'letra_ids')
    def _canjes(self):
        t_inv = sum(line.amount_canje_letra for line in self.invoice_ids)
        t_letr = sum(line.amount_total for line in self.letra_ids)
        self.total_invoice = t_inv + t_letr
        return {}

    def generate(self):
        for element in self:

            list_currency = []
            for line in element.letra_line_ids:
                if not line.currency_id.id in list_currency:
                    list_currency.append(line.currency_id.id)

            for line in element.invoice_ids:
                if not line.currency_id.id in list_currency:
                    list_currency.append(line.currency_id.id)

            if len(list_currency)>1:
                raise ValidationError(_("No se puede manejar dos Tipos de monedas para un Canje"))

            if not element.date and not element.numero:
                raise ValidationError(_("Ingrese una fecha y un Nro de letra para generar"))
            if element.total_invoice <=0:
                raise ValidationError(_("Monto inválido para Canjear por letras"))
            element.letra_line_ids.unlink()
            canje_total = element.total_invoice
            suma_letras = 0
            pterm = element.payment_term_id
            date_due = False
            x=1
            while x<=element.numero:
                date_pass = date_due or element.date
                #pterm_list = pterm.with_context(currency_id=element.company_id.currency_id.id).compute(value=1, date_ref=date_pass)[0]
                pterm_list = pterm.compute(1, date_ref=date_pass, currency=self.currency_id)
                #date_due = max(line[0] for line in pterm_list)
                date_due = pterm_list[0][0]
                canje_letra = round(element.total_invoice/element.numero,2)
                days = (datetime.strptime(date_due, '%Y-%m-%d').date() - element.date).days
                if x == element.numero:
                    canje_letra=element.total_invoice-suma_letras

                # invoice_line_vals = []
                # invoice_vals = self._prepare_invoice(date_due)
                # #line = self._prepare_invoice_line(price_unit=canje_letra, account_id=self.account_id.id)
                # invoice_line_vals.append(
                #     (0, 0, self._prepare_invoice_line(
                #         price_unit=canje_letra,
                #         account_id=self.account_id.id
                #     )),
                # )
                # invoice_vals['line_ids'] += invoice_line_vals
                # moves = self.env['account.move'].sudo().with_context(default_move_type=self.move_type).create(invoice_vals)


                obj = {'days':days,
                       #'date': self.date + timedelta(days= x),
                       'date':date_due,
                       'amount_total':canje_letra,
                       'letra_id':element.id
                }
                self.env['canje.letras.lineas'].create(obj)
                suma_letras +=canje_letra
                x=x+1


    def action_cancel(self):
        moves = self.env['account.move']
        for canje in self:
            if canje.move_id:
                moves += canje.move_id
            for letra in canje.letra_line_ids:
                if letra.state not in ['draft','open']:
                    raise UserError(_('No puede eliminar letras que esten en Estados diferente de Borrador o en Cartera'))

        # First, set the invoices as cancelled and detach the move ids
        for canje in self:
            for line in canje.invoice_ids:
                invoice = line.invoice_id
                for lines_inv in invoice.line_ids:

                    lines = (lines_inv.matched_debit_ids + lines_inv.matched_credit_ids)
                    lines_inv.remove_move_reconcile()
                    # for aml in lines_recon:
                    #     if aml.move_id.id  == self.move_id.id:
                    #         aml.with_context(invoice_id=invoice.id).remove_move_reconcile()
            for letra in canje.letra_line_ids:
                letra.write({'state': 'anulled'})
            #canje.write({'move_id': False})
            #letra_ids

        if moves:
            moves.button_draft()
            #moves.button_cancel()
            moves.with_context(force_delete=True).unlink()

        return True

    def unlink(self):
        for canje in self:
            if canje.state not in ('draft'):
                raise UserError(_('No puedes Eliminar registros que no están en Borrador.'))
            elif canje.name:
                raise UserError(_('No puedes Eliminar una Factura después de haber sido validado (o recibido).'))
        return super(Letras, self).unlink()

    def _prepare_invoice(self, date_due=False):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal = self.journal_id
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': '',
            'move_type': self.move_type,
            #'narration': self.note,
            'currency_id': self.currency_id.id,
            #'campaign_id': self.campaign_id.id,
            #'medium_id': self.medium_id.id,
            #'source_id': self.source_id.id,
            #'invoice_user_id': self.user_id and self.user_id.id,
            #'team_id': self.team_id.id,
            'partner_id': self.partner_id.id,
            #'partner_shipping_id': self.partner_shipping_id.id,
            #'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(self.partner_invoice_id.id)).id,
            #'partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'journal_id': self.journal_id.id,  # company comes from the journal
            'invoice_origin': self.name,
            'invoice_date_due': date_due,
            #'invoice_payment_term_id': self.payment_term_id.id,
            #'payment_reference': self.reference,
            #'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'line_ids': [],
            'company_id': self.company_id.id,
            'canje_id':self.id,
        }
        return invoice_vals


    def _prepare_invoice_line(self, **optional_values):
        """
        Prepare the dict of values to create the new invoice line.

        :param qty: float quantity to invoice
        :param optional_values: any parameter that should be added to the returned invoice line
        """
        self.ensure_one()
        res = {
            'display_type': False,
            'sequence': 0,
            'name': 'Canje',
            #'product_id': self.product_id.id,
            #'product_uom_id': self.product_uom.id,
            'quantity': 1,
            'discount': 0,
            'price_unit': 1,
            'tax_ids': False,
            'account_id': self.account_id.id,
            'exclude_from_invoice_tab':False,
            #'analytic_account_id': self.order_id.analytic_account_id.id,
            #'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            #'sale_line_ids': [(4, self.id)],
        }
        if optional_values:
            res.update(optional_values)
        return res


class LetrasLineas(models.Model):
    _name = 'canje.letras.lineas'
    _description = 'Lineas de Canje de Letras'

    @api.depends('date')
    def _compute_date_pay(self):
        for letra in self:
            if letra.date:
                letra.date_c = letra.date + timedelta(days=8)

    def _get_aml_for_amount_residual(self):
        #self.ensure_one()
        return self.sudo().move_line_id.filtered(lambda l: l.account_id == self.letra_id.account_id)

    @api.depends(
        'currency_id', 'amount_total', 'move_line_id')
    def _compute_residual(self):
        residual = 0.0
        sign = 1
        for line in self._get_aml_for_amount_residual():
            if line.currency_id == self.currency_id:
                residual += line.amount_residual_currency if line.currency_id else line.amount_residual
            else:
                from_currency = line.currency_id or line.company_id.currency_id
                residual += from_currency._convert(line.amount_residual, self.currency_id, line.company_id,
                                                   line.date or fields.Date.today())
        # self.residual = abs(residual)
        digits_rounding_precision = self.currency_id.rounding
        # import pdb; pdb.set_trace()
        if len(self._get_aml_for_amount_residual()) == 0:
            self.reconciled = False
            return
        if float_is_zero(residual, precision_rounding=digits_rounding_precision):
            self.reconciled = True
        else:
            self.reconciled = False

    # @api.multi
    # def _write(self, vals):
    #     pre_not_reconciled = self.filtered(lambda invoice: not invoice.reconciled)
    #     pre_reconciled = self - pre_not_reconciled
    #     res = super(LetrasLineas, self)._write(vals)
    #     reconciled = self.filtered(lambda invoice: invoice.reconciled)
    #     not_reconciled = self - reconciled
    #     (reconciled & pre_reconciled).filtered(lambda invoice: invoice.state == 'open').action_invoice_paid()
    #     # (not_reconciled & pre_not_reconciled).filtered(lambda invoice: invoice.state in ('in_payment', 'paid')).action_invoice_re_open()
    #     return res

    letra_id = fields.Many2one('canje.letras', string='Nro Canje')
    date = fields.Date(string='Fecha de vencimiento', copy=False, required=True,)
    date_c = fields.Date(string='Fecha de cobro', readonly=True, store=True, compute='_compute_date_pay')
    date_disco = fields.Date(string='Fecha de Dscto', readonly=True, store=True)
    currency_id = fields.Many2one('res.currency', string='Moneda', related='letra_id.currency_id')
    name = fields.Char(string='Nro de letra', index=True, readonly=True,  copy=False)
    company_id = fields.Many2one('res.company', string='Compañia', related='letra_id.company_id')
    amount_total = fields.Monetary(string='Total', readonly=True, states={'draft': [('readonly', False)]})
    descargo = fields.Char(string='Descargo', index=True, readonly=False,  copy=False)
    move_line_id = fields.Many2one('account.move.line', string='Apuntes', readonly=True)
    disbursed_move_line_id = fields.Many2one('account.move.line', string='Apunte desembolso', readonly=True)
    residual = fields.Monetary(string='Residual', compute='_compute_residual', store=True, help="Remaining amount due.")
    reconciled = fields.Boolean(related="move_line_id.reconciled", string='Pagado/Conciliado', readonly=True)
    acept = fields.Boolean(string='Aceptada', readonly=True, default=False)
    send_bank = fields.Boolean(string='Enviada al Banco', default=False)
    date_send_bank = fields.Date(string='Fecha Enviada al Banco')
    partner_id = fields.Many2one('res.partner', string='Cliente', related='letra_id.partner_id')
    account_id = fields.Many2one('account.account', string='Cuenta')
    bank_id = fields.Many2one('res.bank', string='Banco', readonly=True)
    numero_pago_descuento = fields.Char(string='Numero Banco', readonly=False,  copy=False)
    state = fields.Selection([
            ('draft','Borrador'),
            ('open', 'Abierto'),
            ('collection','Cobranza'),
            ('discount','Descuento'),
            ('doubtful_collection','Cobranza Dudosa'),
            ('disbursed','Desembolsada'),
            ('paid', 'Pagado'),
            ('renewed','Renovada'),
            ('anulled','Anulado')
        ], string='Estado', index=True, readonly=True, default='draft', copy=False)
    days = fields.Integer(string='dias')
    amount_letters = fields.Char(string='Monto letra', readonly=True, copy=False)
    move_type = fields.Selection(selection=[
        ('out_invoice', 'Cliente'),
        ('in_invoice', 'Proveedor'),
    ], string='Type', related='letra_id.move_type')

    _sql_constraints = [
        ('name', 'unique(name,company_id)', 'Numero unico por compañia'),
    ]



    @api.onchange('days')
    def _onchange_days(self):
        fecha = self.letra_id.date or fields.Date.today()
        self.date = datetime.strptime(str(fecha), '%Y-%m-%d').date() + timedelta(days=self.days)
        #return {}

    def action_invoice_paid(self):
        # Llamadas duplicadas a action_invoice_paid, por lo que eliminamos las que ya se pagaron
        to_pay_invoices = self.filtered(lambda inv: inv.state != 'paid')
        if to_pay_invoices.filtered(lambda inv: inv.state not in ('open', 'in_payment')):
            raise UserError(_('La factura debe ser validada para registrar el pago.'))
        if to_pay_invoices.filtered(lambda inv: not inv.reconciled):
            raise UserError(
                _('No puedes pagar una factura que está parcialmente pagada. Primero debe conciliar las entradas de pago.'))

        for invoice in to_pay_invoices:
            invoice.write({'state': 'paid'})

    def action_regresion(self):

        letra = self
        list_line_move = []
        amount_total = letra.amount_total
        if letra.letra_id.company_id.currency_id != letra.currency_id:
            amount_total = letra.currency_id._convert(letra.amount_total, letra.letra_id.company_id.currency_id,
                                                      letra.letra_id.company_id, letra.letra_id.date)
        obj1 = {
            'name': letra.name,
            'debit': 0,
            'credit': amount_total,
            'account_id': letra.account_id.id,
            'currency_id': letra.currency_id.id,
            'amount_currency': self.amount_total * -1,
            'partner_id': letra.letra_id.partner_id.id,
            # 'invoice_id':name1.invoice_id.id,
        }
        list_line_move.append(obj1)

        obj1 = {
            'name': letra.name,
            'debit': amount_total,
            'credit': 0,
            'account_id': letra.letra_id.journal_id.default_debit_account_id.id,
            'currency_id': letra.currency_id.id,
            'amount_currency': self.amount_total,
            'partner_id': letra.letra_id.partner_id.id,
            # 'letra_id':line.id
        }
        list_line_move.append(obj1)

        conver_list = []
        for line_m in list_line_move:
            if round(line_m['debit'], 2) - round(line_m['credit'], 2) != 0:
                conver_list.append((0, 0, line_m))

        res = {'journal_id': letra.letra_id.journal_id.id,
               'date': fields.Date.today(),
               'ref': 'Regresion cartera',
               # 'period_id':letra.letra_id.journal_id.id,
               'company_id': letra.company_id.id,
               'line_ids': conver_list}

        move = self.env['account.move']
        move_id = move.create(res)
        move_id.post()
        transfer_debit_aml2 = move_id.line_ids.filtered(
            lambda r: r.account_id.id == (letra.letra_id.journal_id.default_debit_account_id.id))
        transfer_debit_aml2.write({'letra_id': letra.id})
        letra.write({'account_id': letra.letra_id.journal_id.default_debit_account_id.id, 'state': 'open',
                     'move_line_id': transfer_debit_aml2.id})


class LetrasLineasFactura(models.Model):
    _name = 'canje.detalle.factura'
    _description = 'Canje de Detalle de Factura'

    @api.depends('date')
    def _compute_date_pay(self):
        if self.date:
            self.date_c = self.date + timedelta(days=8)

    @api.onchange('invoice_id')
    def _default_amount_pay(self):
        amount = self.residual
        if self.letra_id.currency_id.id != self.invoice_id.currency_id.id:
            if self.invoice_id.currency_id.id != self.company_id.currency_id.id:
                # divide
                amount = round(amount * self.letra_id.exchange, 2)
            else:
                amount = round(amount / self.letra_id.exchange, 2)
        self.amount_canje_letra = amount

    invoice_id = fields.Many2one('account.move', string='Factura')
    residual = fields.Monetary(string='Residual', related='invoice_id.amount_residual', currency_field='currency_inv_id')
    amount_canje_letra = fields.Monetary(string='Monto canje', currency_field='currency_id')
    letra_id = fields.Many2one('canje.letras', string='Letra')
    currency_id = fields.Many2one('res.currency', string='Moneda', related='letra_id.currency_id')
    partner_id = fields.Many2one('res.partner', string='Cliente', related='letra_id.partner_id')
    currency_inv_id = fields.Many2one('res.currency', string='Moneda Factura', related='invoice_id.currency_id')
    company_id = fields.Many2one('res.company', string='Compañia', related='letra_id.company_id')
