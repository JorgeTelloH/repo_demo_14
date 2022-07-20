# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class HrEmployeeDocument(models.Model):
    _name = 'hr.employee.document'
    _description = 'Documentos del Empleado'

    @api.constrains('expiry_date')
    def check_expr_date(self):
        for each in self:
            if each.expiry_date:
                exp_date = fields.Date.from_string(each.expiry_date)
                if exp_date < date.today():
                    raise Warning('El Documento ha Caducado!')

    name = fields.Char(string='Documento', required=True, copy=False)
    description = fields.Text(string='Descripción', copy=False)
    expiry_date = fields.Date(string='Fecha caducidad', copy=False)
    employee_ref = fields.Many2one('hr.employee', string='Empleado', invisible=1, copy=False)
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel', 'doc_id', 'attach_id3', string="Adjunto",
                                         help='Puedes Adjuntar la copia de tu(s) Documento(s)', copy=False)
    issue_date = fields.Date(string='Fecha de asunto', default=fields.datetime.now(), copy=False)
    document_type = fields.Many2one('hr.employee.document.type', string="Tipo de documento")
    user_id = fields.Many2one('res.users', string='Usuario', default=lambda self: self.env.user)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    document_count = fields.Integer(compute='_document_count', string='Documentos')

    def _document_count(self):
        for each in self:
            document_ids = self.env['hr.employee.document'].sudo().search([('employee_ref', '=', each.id)])
            each.document_count = len(document_ids)

    def document_view(self):
        self.ensure_one()
        domain = [('employee_ref', '=', self.id)]
        return {
            'name': _('Documentos'),
            'domain': domain,
            'res_model': 'hr.employee.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Clic para crear Nuevo Documento
                        </p>'''),
            'limit': 80,
            'context': "{'default_employee_ref': %s}" % self.id
        }


class HrEmployeeAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_rel = fields.Many2many('hr.employee.document', 'doc_attachment_id', 'attach_id3', 'doc_id',
                                      string="Adjunto", invisible=1)
