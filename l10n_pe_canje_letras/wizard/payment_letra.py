# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LetraPaymentWizard(models.TransientModel):
    _name = "letra.register.payment.wizard"
    _description = 'Wizard de Registro de Pagos de Letras'

    @api.model
    def _default_amount(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letras = self.env['canje.letras.lineas'].browse(active_ids)
        total = 0
        for letra in letras:
            total += letra.amount_total or 0.00
        return total

    @api.model
    def _default_currency(self):
        journal = self.journal_id
        return journal.currency_id or journal.company_id.currency_id or self.env.user.company_id.currency_id


    income_account_id = fields.Many2one('account.account', string='Cuenta ingreso', domain=[('deprecated', '=', False)])
    cost_account_id = fields.Many2one('account.account', string='Cuenta gasto', domain=[('deprecated', '=', False)])
    interest_account_id = fields.Many2one('account.account', string='Cuenta Intereses', domain=[('deprecated', '=', False)])
    bank_account_id = fields.Many2one('account.account', string='Cuenta banco', domain=[('deprecated', '=', False)], readonly=True)
    journal_id = fields.Many2one('account.journal', string='Diario', required=True)
    income_total = fields.Float(string='Total ingreso')
    cost_total = fields.Float(string='Total gasto')
    interest_total = fields.Float(string='Total intereses')
    amount_total = fields.Float(string='Monto de letra', default=_default_amount)
    date = fields.Date(string='Fecha de pago', copy=False, required=True)
    currency_id = fields.Many2one('res.currency', string='Moneda',
                                  required=True, default=_default_currency, track_visibility='always')
    exchange = fields.Float(string='Tipo de cambio', digits='Tipo Cambio', readonly=True)
    company_id = fields.Many2one('res.company', string='Compañia', change_default=True,
                                 required=True, readonly=True,
                                 default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    number_payment = fields.Char(string='Nro operación', required=True)

    @api.onchange('journal_id')
    def _onchange_date(self):
        if not self.journal_id.id:
            return {}
        self.bank_account_id = self.journal_id.default_debit_account_id
        return {}

    @api.onchange('date', 'currency_id')
    def _onchange_date_curr(self):
        # exchange_rate = 0
        # si es una nota de credito de venta o compra
        if self.company_id.currency_id.id == self.currency_id.id:
            self.exchange = 1
        else:
            exchange_rate = self.currency_id.with_context(date=self.date).compute(
                1, self.journal_id.company_id.currency_id, round=False)

            self.exchange = exchange_rate


    @api.onchange('exchange')
    def _onchange_exchange(self):
        context = dict(self._context or {})
        amount_usd = 0
        amount = 0
        active_ids = context.get('active_ids', [])
        letras = self.env['canje.letras.lineas'].browse(active_ids)
        for letra in letras:
            if self.company_id.currency_id.id == letra.currency_id.id:
                amount += letra.amount_total
            else:
                amount_usd += letra.amount_total
        total = (amount_usd) + (amount / self.exchange)
        self.amount_total = total

    def post_payment(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letras = self.env['canje.letras.lineas'].browse(active_ids)
        if self.income_total > 0 and self.income_account_id.id == False:
            raise ValidationError(_('debe ingresar una Cuenta para Ingresos'))

        if self.cost_total > 0 and self.cost_account_id.id == False:
            raise ValidationError(_('debe ingresar una Cuenta para Gasto'))

        if self.interest_total > 0 and self.interest_account_id.id == False:
            raise ValidationError(_('debe ingresar una Cuenta para Intereses'))

        move = self.env['account.move']
        lines = self.create_move_line(letras)

        res = {'journal_id': self.journal_id.id,
               'date': self.date,
               'ref': 'Pago de letra',
               'company_id': self.company_id.id,
               'number_payment': self.number_payment,
               'line_ids': lines}

        move_id = move.create(res)
        move_id.post()

        for letra in letras:
            self.payment_letra(letra, move_id)

    def payment_letra(self, letra, pago_letra):
        transfer_credit_aml = letra.move_line_id
        # transfer_credit_aml = move_id.line_ids.filtered(lambda r: r.account_id == (line.account_id))
        transfer_debit_aml = pago_letra.line_ids.filtered(lambda r: r.account_id.id == (letra.account_id.id))
        (transfer_credit_aml + transfer_debit_aml).reconcile()
        letra.write({'state': 'paid'})

    def create_move_line(self, letra):
        # context = dict(self._context or {})
        # active_ids = context.get('active_ids', [])
        # letra = self.env['canje.letras.lineas'].browse(active_ids)
        # letra_account = letra.letra_id.journal_id.
        list_line_move = []
        move_line = \
        self.env['account.move.line'].search([('name', '=', letra.name), ('move_id', '=', letra.letra_id.move_id.id)])[
            0]

        amount_total = self.amount_total
        monto_banco = self.amount_total + self.income_total - self.cost_total
        income_total = self.income_total
        cost_total = self.cost_total
        interest_total = self.interest_total
        amount_curr = self.amount_total
        currency = self.currency_id.id
        # import pdb; pdb.set_trace()
        if self.company_id.currency_id != self.currency_id:
            # debit, credit, amount_currency, currency_id = self.env['account.move.line'].with_context(date=self.date)._compute_amount_fields(amount_total, self.currency_id, letra.letra_id.company_id.currency_id, letra.currency_id)
            debit, credit, amount_currency, currency_id = self.env['account.move.line'].with_context(date=self.date,
                                                                                                     company_id=self.company_id.id)._compute_amount_fields(
                amount_total, self.currency_id, self.company_id.currency_id)
            cost_debit, cost_credit, cost_amount_currency, cost_currency_id = self.env[
                'account.move.line'].with_context(date=self.date, company_id=self.company_id.id)._compute_amount_fields(
                cost_total, self.currency_id, self.company_id.currency_id)
            interest_debit, interest_credit, interest_amount_currency, interest_currency_id = self.env[
                'account.move.line'].with_context(date=self.date, company_id=self.company_id.id)._compute_amount_fields(
                interest_total, self.currency_id, self.company_id.currency_id)
            income_debit, income_credit, income_amount_currency, income_currency_id = self.env[
                'account.move.line'].with_context(date=self.date, company_id=self.company_id.id)._compute_amount_fields(
                income_total, self.currency_id, self.company_id.currency_id)
            amount_total = debit
            amount_curr = amount_currency
            income_total = income_debit
            cost_total = cost_debit
            # import pdb; pdb.set_trace()
            if letra.currency_id != self.currency_id:
                # amount_total = self.env['account.move.line'].search([('letra_id','=',letra.id)]).debit
                amount_total = letra.move_line_id.debit
                if amount_total == 0:
                    raise ValidationError(_('Asiento no encontrado o en cero (0)'))
                # amount_total = self.amount_total
                debit, credit, amount_currency, currency_id = self.env['account.move.line'].with_context(
                    date=letra.letra_id.date, company_id=letra.letra_id.company_id.id)._compute_amount_fields(
                    amount_total, self.journal_id.currency_id, letra.letra_id.company_id.currency_id)
                cost_debit, cost_credit, cost_amount_currency, cost_currency_id = self.env[
                    'account.move.line'].with_context(date=letra.letra_id.date,
                                                      company_id=letra.letra_id.company_id.id)._compute_amount_fields(
                    cost_total, letra.currency_id, self.journal_id.currency_id)
                interest_debit, interest_credit, interest_amount_currency, interest_currency_id = self.env[
                    'account.move.line'].with_context(date=letra.letra_id.date,
                                                      company_id=letra.letra_id.company_id.id)._compute_amount_fields(
                    interest_total, letra.currency_id, self.journal_id.currency_id)
                income_debit, income_credit, income_amount_currency, income_currency_id = self.env[
                    'account.move.line'].with_context(date=letra.letra_id.date,
                                                      company_id=letra.letra_id.company_id.id)._compute_amount_fields(
                    income_total, letra.currency_id, self.journal_id.currency_id)
                amount_total = debit
                income_total = income_debit
                cost_total = cost_debit

        if (letra.letra_id.currency_id != self.currency_id) and (
                letra.letra_id.company_id.currency_id == self.journal_id.currency_id):
            debit, credit, amount_currency, currency_id = self.env['account.move.line'].with_context(
                date=letra.letra_id.date, company_id=letra.letra_id.company_id.id)._compute_amount_fields(amount_total,
                                                                                                          letra.currency_id,
                                                                                                          letra.letra_id.company_id.currency_id,
                                                                                                          letra.currency_id)
            amount_total = debit
            amount_curr = False
            currency = self.currency_id.id

            # amount_total = letra.currency_id._convert(amount_total, letra.letra_id.company_id.currency_id, letra.letra_id.company_id, self.date)
            # amount_total = letra.currency_id._convert(monto_banco, letra.letra_id.company_id.currency_id, letra.letra_id.company_id, self.date)
            # income_total = letra.currency_id._convert(income_total, letra.letra_id.company_id.currency_id, letra.letra_id.company_id, self.date)
            # cost_total = letra.currency_id._convert(cost_total, letra.letra_id.company_id.currency_id, letra.letra_id.company_id, self.date)

            # amount_total = letra.currency_id.with_context(date=self.date).compute(amount_total, letra.letra_id.company_id.currency_id)

            # income_total = letra.currency_id.with_context(date=self.date).compute(income_total, letra.letra_id.company_id.currency_id)
            # cost_total = letra.currency_id.with_context(date=self.date).compute(cost_total, letra.letra_id.company_id.currency_id)
        obj1 = {
            'name': letra.name,
            'debit': 0,
            'credit': amount_total,
            'account_id': letra.move_line_id.account_id.id,
            'currency_id': letra.currency_id.id,
            'amount_currency': self.amount_total * -1,
            'partner_id': letra.letra_id.partner_id.id,
            # 'invoice_id':name1.invoice_id.id,
        }
        list_line_move.append(obj1)

        obj1 = {
            'name': letra.name,
            'debit': amount_total + income_total - cost_total,
            'credit': 0,
            'account_id': self.journal_id.default_debit_account_id.id,
            'currency_id': currency,
            'amount_currency': amount_curr,
            'partner_id': letra.letra_id.partner_id.id,
            # 'letra_id':line.id
        }
        list_line_move.append(obj1)

        if self.income_total > 0:
            obj1 = {
                'name': letra.name,
                'debit': 0,
                'credit': income_total,
                'account_id': self.income_account_id.id,
                'currency_id': letra.currency_id.id,
                'amount_currency': self.income_total * -1,
                'partner_id': letra.letra_id.partner_id.id,
            }
            list_line_move.append(obj1)

        if self.cost_total > 0:
            obj1 = {
                'name': letra.name,
                'debit': cost_total,
                'credit': 0,
                'account_id': self.cost_account_id.id,
                'currency_id': letra.currency_id.id,
                'amount_currency': self.cost_total,
                'partner_id': letra.letra_id.partner_id.id,
            }
            list_line_move.append(obj1)

        conver_list = []
        for line_m in list_line_move:
            if round(line_m['debit'], 2) - round(line_m['credit'], 2) != 0:
                conver_list.append((0, 0, line_m))

        return conver_list


class LetracollectionWizard(models.TransientModel):
    _name = "letra.register.wizard"
    _description = 'Wizard de Registro de Letras'

    @api.model
    def _default_amount(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letras = self.env['canje.letras.lineas'].browse(active_ids)
        total = 0
        for letra in letras:
            total += letra.amount_total or 0.00
        return total

    journal_id = fields.Many2one('account.journal', string='Diario')
    amount_total = fields.Float(string='Monto de letra', readonly=True, default=_default_amount)
    date = fields.Date(string='Fecha', copy=False, required=True)

    @api.onchange('date')
    def _onchange_date(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letra = self.env['canje.letras.lineas'].browse(active_ids)[0]
        period = self.env['date.range'].search(
            [('date_start', '<=', self.date), ('date_end', '>=', self.date), ('company_id', '=', letra.company_id.id)])

    def post_collect(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letra = self.env['canje.letras.lineas'].browse(active_ids)

        move = self.env['account.move']
        lines = self.create_move_line(letra)

        res = {'journal_id': self.journal_id.id,
               'date': self.date,
               'ref': 'Letra en cobranza',
               'company_id': letra.company_id.id,
               'line_ids': lines}

        move_id = move.create(res)
        move_id.post()

        self.collect_letra(letra, move_id)

    def create_move_line(self, letra):
        list_line_move = []
        move_line = \
        self.env['account.move.line'].search([('name', '=', letra.name), ('move_id', '=', letra.letra_id.move_id.id)])[
            0]
        debit, credit, amount_currency, currency_id = self.env['account.move.line'].with_context(date=self.date,
                                                                                                 company_id=letra.company_id.id)._compute_amount_fields(
            self.amount_total, letra.currency_id, letra.company_id.currency_id)
        debit1, credit1, amount_currency1, currency_id1 = self.env['account.move.line'].with_context(date=self.date,
                                                                                                     company_id=letra.company_id.id)._compute_amount_fields(
            1, letra.currency_id, letra.company_id.currency_id)

        obj1 = {
            'name': letra.name,
            'debit': 0,
            'credit': debit,
            'account_id': letra.account_id.id,
            'currency_id': letra.currency_id.id,
            'amount_currency': amount_currency * -1,
            'partner_id': letra.letra_id.partner_id.id,
            'type_document': self.journal_id.type_document.id,
            'value_change': debit1,
            'date_issue': letra.date,
            # 'invoice_id':name1.invoice_id.id,
        }
        list_line_move.append(obj1)

        obj1 = {
            'name': letra.name,
            'debit': debit,
            'credit': 0,
            'account_id': self.journal_id.collection_account_id.id,
            'currency_id': letra.currency_id.id,
            'amount_currency': amount_currency,
            'partner_id': letra.letra_id.partner_id.id,
            'type_document': self.journal_id.type_document.id,
            'value_change': debit1,
            'date_issue': letra.date,
            # 'letra_id':line.id
        }
        list_line_move.append(obj1)

        conver_list = []
        for line_m in list_line_move:
            if round(line_m['debit'], 2) - round(line_m['credit'], 2) != 0:
                conver_list.append((0, 0, line_m))

        return conver_list

    def collect_letra(self, letra, pago_letra):

        transfer_credit_aml = letra.move_line_id
        # transfer_credit_aml = move_id.line_ids.filtered(lambda r: r.account_id == (line.account_id))
        transfer_debit_aml = pago_letra.line_ids.filtered(lambda r: r.account_id.id == (letra.account_id.id))
        transfer_debit_aml2 = pago_letra.line_ids.filtered(
            lambda r: r.account_id.id == (self.journal_id.collection_account_id.id))
        # import pdb; pdb.set_trace()
        (transfer_credit_aml + transfer_debit_aml).reconcile()
        type_d = self._context.get('default_type')
        transfer_debit_aml2.write({'letra_id': letra.id})
        letra.write({'state': type_d, 'account_id': self.journal_id.default_debit_account_id.id,
                     'move_line_id': transfer_debit_aml2.id})


class LetraDiscountWizard(models.TransientModel):
    _name = "letra.discount.wizard"
    _description = 'Wizard de Descuento de Letras'

    @api.model
    def _default_amount(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letras = self.env['canje.letras.lineas'].browse(active_ids)
        total = 0
        for letra in letras:
            total += letra.amount_total or 0.00
        return total

    @api.model
    def _default_account(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letra = self.env['canje.letras.lineas'].browse(active_ids)[0]
        # import pdb; pdb.set_trace()
        return letra.letra_id.journal_id.discount_account_id.id or False

    @api.model
    def _default_currency(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letra = self.env['canje.letras.lineas'].browse(active_ids)[0]
        return letra.currency_id or self.env.user.company_id.currency_id


    # journal_id = fields.Many2one('account.journal', string='Diario', required=True)
    # journal_bank_id = fields.Many2one('account.journal', string='Banco', domain=[('type', 'in', ('bank', 'cash'))], required=True)
    account_id = fields.Many2one('account.account', string='Cuenta', required=True, default=_default_account)
    amount_total = fields.Float(string='Monto de letra', readonly=True, default=_default_amount, required=True)
    date = fields.Date(string='Fecha', copy=False)

    @api.onchange('date')
    def _onchange_date(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letra = self.env['canje.letras.lineas'].browse(active_ids)[0]


    def post_collect(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letras = self.env['canje.letras.lineas'].browse(active_ids)
        for letra in letras:
            if letra.state != 'open':
                raise ValidationError(_('La letra tiene que estar en cartera'))
            if letra.send_bank == False:
                raise ValidationError(_('La letra aun no ha sido enviada al Banco'))

        lines = self.create_move_line(letras)

        res = {'journal_id': letra.letra_id.journal_id.id,
               'date': fields.Date.today(),
               'ref': 'Letra en descuento',
               'company_id': letra.company_id.id,
               'line_ids': lines}

        move = self.env['account.move']
        move_id = move.create(res)
        move_id.post()
        for letra in letras:
            self.collect_letra(letra, move_id)

    def create_move_line(self, letras):
        list_line_move = []
        # move_line = self.env['account.move.line'].search([('name','=',letra.name),('move_id','=',letra.letra_id.move_id.id)])[0]
        # amount_total = letra.amount_total
        # if letra.letra_id.company_id.currency_id != letra.currency_id:
        # amount_total = letra.currency_id._convert(amount_total, letra.letra_id.company_id.currency_id, letra.letra_id.company_id, letra.letra_id.date)
        # amount_total = letra.currency_id.with_context(date=letra.letra_id.date).compute(amount_total, letra.letra_id.company_id.currency_id)
        for letra in letras:
            debit, credit, amount_currency, currency_id = self.env['account.move.line'].with_context(date=self.date,
                                                                                                     company_id=letra.company_id.id)._compute_amount_fields(
                letra.amount_total * -1, letra.currency_id, letra.company_id.currency_id)
            obj1 = {
                'name': letra.name,
                'debit': 0,
                'credit': credit,
                'account_id': letra.account_id.id,
                'currency_id': currency_id,
                'amount_currency': amount_currency,
                'partner_id': letra.letra_id.partner_id.id,
                # 'invoice_id':name1.invoice_id.id,
            }
            list_line_move.append(obj1)

            debit, credit, amount_currency, currency_id = self.env['account.move.line'].with_context(date=self.date,
                                                                                                     company_id=letra.company_id.id)._compute_amount_fields(
                letra.amount_total, letra.currency_id, letra.company_id.currency_id)
            obj1 = {
                'name': letra.name,
                'debit': debit,
                'credit': 0,
                'account_id': self.account_id.id,
                'currency_id': currency_id,
                'amount_currency': amount_currency,
                'partner_id': letra.letra_id.partner_id.id,
                # 'letra_id':line.id
            }
            list_line_move.append(obj1)

        conver_list = []
        for line_m in list_line_move:
            if round(line_m['debit'], 2) - round(line_m['credit'], 2) != 0:
                conver_list.append((0, 0, line_m))

        return conver_list

    def collect_letra(self, letra, pago_letra):

        # transfer_credit_aml = self.env['account.move.line'].search([('name','=',letra.name),('move_id','=',letra.letra_id.move_id.id)])[0]

        transfer_credit_aml = letra.move_line_id
        # transfer_credit_aml = move_id.line_ids.filtered(lambda r: r.account_id == (line.account_id))
        transfer_debit_aml = pago_letra.line_ids.filtered(
            lambda r: r.account_id.id == (letra.account_id.id) and r.name == letra.name)
        transfer_debit_aml2 = pago_letra.line_ids.filtered(
            lambda r: r.account_id.id == (self.account_id.id) and r.name == letra.name)
        # import pdb; pdb.set_trace()
        (transfer_credit_aml + transfer_debit_aml).reconcile()
        type_d = self._context.get('default_type')
        transfer_debit_aml2.write({'letra_id': letra.id})
        letra.write({'state': type_d, 'account_id': self.account_id.id,
                     'move_line_id': transfer_debit_aml2.id,
                     'date_disco': self.date})


class LetraDisbursedWizard(models.TransientModel):
    _inherit = "letra.register.payment.wizard"
    _name = "letra.disbursed.wizard"

    @api.model
    def _default_account(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letra = self.env['canje.letras.lineas'].browse(active_ids)[0]
        # import pdb; pdb.set_trace()
        return letra.letra_id.journal_id.disbursed_collection_debit_account_id.id or False

    @api.model
    def _default_account_cp(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letra = self.env['canje.letras.lineas'].browse(active_ids)[0]
        # import pdb; pdb.set_trace()
        return letra.letra_id.journal_id.disbursed_collection_credit_account_id.id or False

    @api.model
    def _default_account_int(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letra = self.env['canje.letras.lineas'].browse(active_ids)[0]
        # import pdb; pdb.set_trace()
        return letra.letra_id.journal_id.disbursed_collection_interest_account_id.id or False

    @api.model
    def _default_amount(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        amount = 0
        letras = self.env['canje.letras.lineas'].browse(active_ids)
        for letra in letras:
            amount += letra.amount_total
        return amount

    journal_id = fields.Many2one('account.journal', string='Diario', required=True, domain=[('type', '=', 'bank')])
    income_account_id = fields.Many2one('account.account', string='Cuenta por pagar', 
        domain=[('deprecated', '=', False)], default=_default_account_cp)
    cost_account_id = fields.Many2one('account.account', string='Cuenta de gasto', 
        domain=[('deprecated', '=', False)], default=_default_account)
    amount_total = fields.Float(string='Monto de desembolso', default=_default_amount)
    interest_account_id = fields.Many2one('account.account', string='Cuenta Intereses', 
        domain=[('deprecated', '=', False)], default=_default_account_int)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica')

    def post_payment(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letras = self.env['canje.letras.lineas'].browse(active_ids)
        if self.income_total > 0 and self.income_account_id.id == False:
            raise ValidationError(_('Debe ingresar una Cuenta de Ingresos'))

        if self.cost_total > 0 and self.cost_account_id.id == False:
            raise ValidationError(_('Debe ingresar una Cuenta de Gasto'))

        move = self.env['account.move']
        lines = self.create_move_line(letras)

        res = {'journal_id': self.journal_id.id,
               'date': self.date,
               'ref': 'Desembolso de Letras en Descuento',
               'company_id': self.company_id.id,
               'number_payment': self.number_payment,
               'line_ids': lines}

        move_id = move.create(res)
        move_id.post()
        for letra in letras:
            self.payment_letra(letra, move_id)

    # def payment_letra(self,letra,pago_letra):
    #     transfer_credit_aml = letra.move_line_id
    #     #transfer_credit_aml = move_id.line_ids.filtered(lambda r: r.account_id == (line.account_id))
    #     #transfer_debit_aml = pago_letra.line_ids.filtered(lambda r: r.account_id.id == (letra.account_id.id))
    #     #(transfer_credit_aml+transfer_debit_aml).reconcile()
    #     type_d = self._context.get('default_type')
    #     letra.write({'state':type_d})

    def create_move_line(self, letras):

        amount_total = self.amount_total - self.cost_total - self.interest_total
        cost_total = self.cost_total
        amount_curr = self.amount_total
        currency = self.currency_id.id
        interest_total = self.interest_total
        list_line_move = []
        # import pdb; pdb.set_trace()
        # if self.company_id.currency_id != self.currency_id:
        #     debit, credit, amount_currency, currency_id = self.env['account.move.line'].with_context(date=self.date,company_id=self.company_id.id)._compute_amount_fields(amount_total, self.currency_id, self.company_id.currency_id)
        #     cost_debit, cost_credit, cost_amount_currency, cost_currency_id = self.env['account.move.line'].with_context(date=self.date,company_id=self.company_id.id)._compute_amount_fields(cost_total, self.currency_id, self.company_id.currency_id)
        #     amount_total = debit
        #     amount_curr = amount_currency
        #     cost_total = cost_debit
        # if letra.currency_id != self.currency_id:
        #     debit, credit, amount_currency, currency_id = self.env['account.move.line'].with_context(date=letra.letra_id.date,company_id=letra.letra_id.company_id.id)._compute_amount_fields(amount_total, self.journal_id.currency_id, letra.letra_id.company_id.currency_id)
        #     cost_debit, cost_credit, cost_amount_currency, cost_currency_id = self.env['account.move.line'].with_context(date=letra.letra_id.date,company_id=letra.letra_id.company_id.id)._compute_amount_fields(cost_total, letra.currency_id, self.journal_id.currency_id)
        #     amount_total = debit
        #     cost_total = cost_debit

        for letra in letras:
            debit, credit, amount_currency, currency_id = self.env['account.move.line'].with_context(date=self.date,
                                                                                                     company_id=self.company_id.id)._compute_amount_fields(
                letra.amount_total * -1, letra.currency_id, self.company_id.currency_id)
            obj1 = {
                'name': letra.name,
                'debit': 0,
                'credit': credit,
                'account_id': self.income_account_id.id,
                'currency_id': currency_id or False,
                'amount_currency': amount_currency,
                'partner_id': letra.letra_id.partner_id.id,
                # 'invoice_id':name1.invoice_id.id,
            }
            list_line_move.append(obj1)

        debit, credit, amount_currency, currency_id = self.env['account.move.line'].with_context(date=self.date,
                                                                                                 company_id=self.company_id.id)._compute_amount_fields(
            amount_total, self.currency_id, self.company_id.currency_id)
        cost_debit, cost_credit, cost_amount_currency, cost_currency_id = self.env['account.move.line'].with_context(
            date=self.date, company_id=self.company_id.id)._compute_amount_fields(cost_total, self.currency_id,
                                                                                  self.company_id.currency_id)
        interest_debit, interest_credit, interest_amount_currency, interest_currency_id = self.env[
            'account.move.line'].with_context(date=self.date, company_id=self.company_id.id)._compute_amount_fields(
            interest_total, self.currency_id, self.company_id.currency_id)

        obj1 = {
            'name': self.number_payment,
            'debit': debit,
            'credit': 0,
            'account_id': self.journal_id.default_debit_account_id.id,
            'currency_id': currency_id or False,
            'amount_currency': amount_currency,
            'partner_id': letra.letra_id.partner_id.id,
            # 'letra_id':line.id
        }
        list_line_move.append(obj1)

        obj1 = {
            'name': self.number_payment,
            'debit': cost_debit,
            'credit': 0,
            'account_id': self.cost_account_id.id,
            'currency_id': cost_currency_id or False,
            'amount_currency': cost_amount_currency,
            'partner_id': letra.letra_id.partner_id.id,
            'account_analytic_id': self.account_analytic_id.id or False
            # 'letra_id':line.id
        }
        list_line_move.append(obj1)

        obj1 = {
            'name': self.number_payment,
            'debit': interest_debit,
            'credit': 0,
            'account_id': self.interest_account_id.id,
            'currency_id': cost_currency_id or False,
            'amount_currency': interest_amount_currency,
            'partner_id': letra.letra_id.partner_id.id,
            'account_analytic_id': self.account_analytic_id.id or False
            # 'letra_id':line.id
        }
        list_line_move.append(obj1)

        balance = 0
        count = 1
        for elements in list_line_move:
            balance += elements['debit'] - elements['credit']
            if len(list_line_move) == count:
                if balance != 0:
                    elements['debit'] = round(elements['debit'] + (balance * -1), 2)

            count += 1

        # import pdb; pdb.set_trace()
        conver_list = []
        for line_m in list_line_move:
            if round(line_m['debit'], 2) - round(line_m['credit'], 2) != 0:
                conver_list.append((0, 0, line_m))

        return conver_list

    def payment_letra(self, letra, pago_letra):

        transfer_debit_aml2 = pago_letra.line_ids.filtered(
            lambda r: r.account_id.id == (self.income_account_id.id) and r.name == letra.name)
        type_d = self._context.get('default_type')
        transfer_debit_aml2.write({'letra_id': letra.id})
        letra.write({'state': type_d, 'disbursed_move_line_id': transfer_debit_aml2.id})


class LetraDisbursedWizard(models.TransientModel):
    _inherit = "letra.register.payment.wizard"
    _name = "letra.collection.wizard"

    @api.model
    def _default_amount(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        amount = 0
        letras = self.env['canje.letras.lineas'].browse(active_ids)
        for letra in letras:
            amount += letra.amount_total
        return amount

    journal_id = fields.Many2one('account.journal', string='Diario', required=True, domain=[('type', '=', 'bank')])

    def post_payment(self):

        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letras = self.env['canje.letras.lineas'].browse(active_ids)

        move = self.env['account.move']
        lines = self.create_move_line(letras)

        res = {'journal_id': self.journal_id.id,
               'date': self.date,
               'ref': 'Cancelacion de letra en cobranza',
               'company_id': self.company_id.id,
               'number_payment': self.number_payment,
               'line_ids': lines}

        move_id = move.create(res)
        move_id.post()
        for letra in letras:
            self.payment_letra(letra, move_id)

    def create_move_line(self, letras):

        amount_total = self.amount_total
        amount_curr = self.amount_total
        currency = self.currency_id.id
        list_line_move = []
        total_credit = 0
        total_amount_currency = 0

        for letra in letras:
            if letra.state != 'collection':
                raise ValidationError(_('Solo puede procesar letras en Cobranza'))
            debit, credit, amount_currency, currency_id = self.env['account.move.line'].with_context(date=self.date,
                                                                                                     company_id=self.company_id.id)._compute_amount_fields(
                letra.amount_total * -1, letra.currency_id, self.company_id.currency_id)
            obj1 = {
                'name': letra.name,
                'debit': 0,
                'credit': credit,
                'account_id': letra.move_line_id.account_id.id,
                'currency_id': currency_id or False,
                'amount_currency': amount_currency,
                'partner_id': letra.letra_id.partner_id.id,
                'type_document': letra.journal_id.type_document.id,
                'value_change': self.exchange,
                'date_issue': letra.date,
                # 'invoice_id':name1.invoice_id.id,
            }
            list_line_move.append(obj1)
            total_credit += abs(credit)
            total_amount_currency += abs(amount_currency)

        obj1 = {
            'name': self.number_payment,
            'debit': total_credit,
            'credit': 0,
            'account_id': self.journal_id.default_debit_account_id.id,
            'currency_id': currency_id or False,
            'amount_currency': total_amount_currency,
            'partner_id': False,
            'type_document': self.journal_id.type_document.id,
            'value_change': self.exchange,
            'date_issue': self.date,
            # 'letra_id':line.id
        }
        list_line_move.append(obj1)

        balance = 0
        count = 1
        for elements in list_line_move:
            balance += elements['debit'] - elements['credit']
            if len(list_line_move) == count:
                if balance != 0:
                    elements['debit'] = round(elements['debit'] + (balance * -1), 2)

            count += 1

        conver_list = []
        for line_m in list_line_move:
            if round(line_m['debit'], 2) - round(line_m['credit'], 2) != 0:
                conver_list.append((0, 0, line_m))

        return conver_list

    def payment_letra(self, letra, pago_letra):

        transfer_debit_aml = letra.move_line_id
        transfer_debit_aml2 = pago_letra.line_ids.filtered(
            lambda r: r.account_id.id == (letra.move_line_id.id) and r.name == letra.name)
        (transfer_debit_aml2 + transfer_debit_aml).reconcile()
        transfer_debit_aml2.write({'letra_id': letra.id})
        letra.write({'state': 'paid'})


class LetraSendBankWizard(models.TransientModel):
    _name = "letra.send.bank.wizard"
    _description = 'Wizard de envio de Letras al Banco'

    bank_id = fields.Many2one('res.bank', string='Banco', require=True)

    date_send_bank = fields.Date(string='Fecha enviada al banco', require=True)

    def send_bank(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letras = self.env['canje.letras.lineas'].browse(active_ids)
        for letra in letras:
            if letra.state == "open":
                letra.write({'send_bank': True, 'bank_id': self.bank_id.id, 'date_send_bank': self.date_send_bank})
            else:
                raise ValidationError(_('La letra tiene que estar en cartera'))


class LetraPayMAsivekWizard(models.TransientModel):
    _name = "letra.pay.masive.wizard"
    _description = 'Wizard de Pago masivo de Letras'

    payment_date = fields.Date(string="Fecha de pago")
    total_amount = fields.Float(string="Monto Total", readonly=True)
    advance_amount = fields.Monetary(string='Monto de pago', required=True)
    currency_id = fields.Many2one('res.currency', string='Moneda', required=True, default=lambda self: self.env.user.company_id.currency_id)
    multi_currency_id = fields.Many2one('res.currency', string='Multi-moneda')
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Compañia', readonly=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Método de pago', oldname="payment_method", 
        help="Manual: Reciba pagos en efectivo, cheque o cualquier otro método.\n" \
            "Electronico: Reciba pagos a través de un canal de pago con una transacción de tarjeta del cliente en línea (token de pago).\n" \
            "Cheque: Pague la factura con cheque e imprímala desde el Sistema.\n" \
            "Depósito por Lote: Envie varios cheques de clientes generando un depósito por lotes para enviar a su banco. Al codificar el extracto bancario, se sugiere conciliar la transacción con el depósito por lotes. Para habilitar el depósito por lotes, se debe instalar el módulo account_batch_payment.\n" \
            "SEPA Transferencia Creditor: Pague la factura desde un archivo de transferencia de crédito SEPA que envíe a su banco. Para habilitar la transferencia de crédito sepa, se debe instalar el módulo account_sepa")
    payment_type = fields.Selection([('outbound', 'Enviar dinero'), ('inbound', 'Recibir dinero')], string='Tipo de Pago')
    journal_id = fields.Many2one('account.journal', string='Diario')
    company_curr_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Moneda de la Compañia', readonly=True)
    number_payment = fields.Char( string='Nro Pago')

    @api.model
    def default_get(self, default_fields):
        res = super(LetraPayMAsivekWizard, self).default_get(default_fields)
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letras = self.env['canje.letras.lineas'].browse(active_ids)
        amount_local = 0
        for letra in letras:
            if letra.currency_id != letra.company_id.currency_id:
                amount_local += letra.currency_id._convert(letra.amount_total, letra.company_id.currency_id,
                                                           letra.company_id, fields.Date.today())
            else:
                amount_local += letra.amount_total
        payment_data = {
            'advance_amount': amount_local,
            'payment_date': fields.Date.today(),
        }
        res.update(payment_data)
        if 'journal_id' not in res:
            res['journal_id'] = self.env['account.journal'].search(
                [('company_id', '=', self.env.user.company_id.id), ('type', 'in', ('bank', 'cash'))], limit=1).id
        return res

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if self.payment_type:
            return {'domain': {'payment_method_id': [('payment_type', '=', self.payment_type)]}}

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            payment_type = self.payment_type in ('inbound', 'transfer') and 'inbound' or 'inbound'
            return {'domain': {
                'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)]}}
        return {}

    @api.onchange('payment_date')
    def _onchange_date(self):
        context = dict(self._context or {})
        # active_ids = context.get('active_ids', [])
        # letra = self.env['canje.letras.lineas'].browse(active_ids)[0]

        # self.advance_amount = self._compute_payment_amount(self.currency_id, self.journal_id, self.payment_date)

    @api.onchange('currency_id')
    def _onchange_currency(self):
        if self.currency_id and self.journal_id and self.payment_date:
            advance_amount = abs(self._compute_payment_amount(self.currency_id, self.journal_id, self.payment_date))
            self.advance_amount = advance_amount
        else:
            self.advance_amount = 0.0

        if self.journal_id:  # TODO: only return if currency differ?
            return

        # Set by default the first liquidity journal having this currency if exists.
        domain = [('type', 'in', ('bank', 'cash')),
                  ('currency_id', '=', self.currency_id.id),
                  ('company_id', '=', self.company_id.id), ]
        journal = self.env['account.journal'].search(domain, limit=1)
        if journal:
            return {'value': {'journal_id': journal.id}}

    @api.model
    def _compute_payment_amount(self, currency, journal, date):
        company = journal.company_id
        date = date or fields.Date.today()
        total = 0.0
        if company.currency_id == currency:
            if self.advance_amount == 0.0:
                total += self.advance_amount
            else:
                if self.multi_currency_id:
                    total += self.multi_currency_id._convert(self.advance_amount, company.currency_id, company, date)
                    self.multi_currency_id = False
                else:
                    total += company.currency_id._convert(self.advance_amount, currency, company, date)
        else:
            total += company.currency_id._convert(self.advance_amount, currency, company, date)
            self.multi_currency_id = currency
        return total

    @api.model
    def _compute_payment_individual(self, currency, journal, date, amount, letra):
        company = journal.company_id
        date = date or fields.Date.today()
        total = 0.0
        if letra.currency_id == currency:
            if self.advance_amount == 0.0:
                total += self.advance_amount
            else:
                if self.multi_currency_id:
                    total += self.multi_currency_id._convert(amount, company.currency_id, company, date)
                else:
                    total += company.currency_id._convert(amount, currency, company, date)
        else:
            total += company.currency_id._convert(amount, currency, company, date)
        return total

    def pay_masive(self):
        company = self.journal_id.company_id
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        letras = self.env['canje.letras.lineas'].browse(active_ids)
        list_save = []
        total_debit = 0
        total_amount_currency = 0
        for letra in letras:
            if letra.state in ["open", "disbursed"]:
                # amount_letra = self._compute_payment_individual(self.currency_id, self.journal_id, self.payment_date, letra.amount_total, letra)
                debit, credit, amount_currency, currency_id = self.env['account.move.line'].with_context(
                    date=self.payment_date, company_id=self.company_id.id)._compute_amount_fields(
                    letra.amount_total * -1, self.currency_id, self.company_id.currency_id)
                obj1 = {
                    'name': letra.name,
                    'debit': 0,
                    'credit': credit,
                    'account_id': letra.move_line_id.account_id.id,
                    'currency_id': currency_id or self.currency_id.id,
                    'amount_currency': amount_currency,
                    'partner_id': letra.letra_id.partner_id.id,
                    # 'invoice_id':name1.invoice_id.id,
                }
                list_save.append((0, 0, obj1))
                total_debit += credit
                total_amount_currency += amount_currency

                obj2 = {
                    'name': letra.name,
                    'debit': credit,
                    'credit': 0,
                    'account_id': letra.disbursed_move_line_id.account_id.id or letra.letra_id.journal_id.disbursed_collection_credit_account_id.id,
                    'currency_id': currency_id or self.currency_id.id,
                    'amount_currency': amount_currency * -1,
                    'partner_id': letra.letra_id.partner_id.id,
                    # 'invoice_id':name1.invoice_id.id,
                }
                list_save.append((0, 0, obj2))


            else:
                raise ValidationError(_('La letra tiene que estar en Cartera o Desembolsada'))

        res = {'journal_id': self.journal_id.id,
               'date': self.payment_date,
               'ref': 'Cancelación de letra',
               'company_id': company.id,
               'number_payment': self.number_payment,
               'line_ids': list_save}

        move = self.env['account.move']
        move_id = move.create(res)
        move_id.post()

        for letra in letras:
            self.payment_letra(letra, move_id)

    def payment_letra(self, letra, pago_letra):
        transfer_credit_aml = letra.move_line_id
        # transfer_credit_aml = move_id.line_ids.filtered(lambda r: r.account_id == (line.account_id))
        transfer_debit_aml = pago_letra.line_ids.filtered(
            lambda r: r.account_id.id == (letra.move_line_id.account_id.id) and r.name == letra.name)
        (transfer_credit_aml + transfer_debit_aml).reconcile()
        if letra.disbursed_move_line_id.id:
            transfer_disb_credit_aml = letra.disbursed_move_line_id
            transfer_disb_debit_aml = pago_letra.line_ids.filtered(
                lambda r: r.account_id.id == (letra.disbursed_move_line_id.account_id.id) and r.name == letra.name)
            (transfer_disb_credit_aml + transfer_disb_debit_aml).reconcile()
        letra.write({'state': 'paid'})

