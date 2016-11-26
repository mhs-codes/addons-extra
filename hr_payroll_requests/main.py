from openerp import models, api, fields

class Test(models.Model):
    _name = 'test.test'

    lines_selected = fields.One2many('res.partner', 'test')
    lines_unselected = fields.One2many('res.partner', 'test')
    sel = fields.Boolean()

class Partnr(models.Model):
    _inherit = 'res.partner'

    test = fields.Many2one('test.test')
    sel = fields.Boolean()