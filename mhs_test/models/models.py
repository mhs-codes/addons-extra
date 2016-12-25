# -*- encoding: utf-8 -*-

from openerp import models, fields, api

class Test(models.Model):
    _name = 'mhs.test'

    name = fields.Char()
    mode = fields.Selection([
                    ('a', 'A'),
                    ('b', 'B'),
                    ('c', 'C'),
                    ('d', 'D'),
                    ])
    partner = fields.Many2one('res.partner')
    employees = fields.Many2many('hr.employee')

    @api.multi
    def launch_wiz(self):
        return self.env['mhs.test.wiz'].view_wizard()

class TestWiz(models.TransientModel):
    _name = 'mhs.test.wiz'

    name = fields.Char()
    mode = fields.Selection([
                    ('a', 'A'),
                    ('b', 'B'),
                    ('c', 'C'),
                    ('d', 'D'),
                    ])
    partner = fields.Many2one('res.partner')
    employees = fields.Many2many('hr.employee')

    @api.multi
    def apply(self):
        print self.read()
        print self.env.context
        return 1

    @api.model
    def view_wizard(self):
        view = {
                'name': 'Test Wiz',
                'res_model': 'mhs.test.wiz',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'view_mode': 'form,tree',
                }
        return view