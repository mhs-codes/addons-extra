from openerp import models, api, fields

class Test(models.Model):
    _name = 'test.test'

    lines_selected = fields.One2many('res.partner')
    lines_unselected = fields.One2many('res.partner')
    sel = fields.Boolean()

class Partnr(models.Model):
    _inherit = 'res.partner'

    sel = fields.Boolean()