from openerp import api, models, fields, tools
from openerp.exceptions import UserError, ValidationError
import time
from datetime import datetime

class SalaryAdvancePay(models.Model):

    _inherit = 'hr.payslip'

    # advance_pay = fields.Boolean(default=False)
    # amount_advance = fields.Float('Advance amount', default=99)
    # amount_normal_pay = fields.Float(string='Original Salary(used to show while entering advance payment)')
    amount_payslip_total = fields.Float(compute='get_payslip_total')
    # line_ids_normal = fields.One2many('hr.payslip.line', 'slip_id', store=False)
    # payslip_advance_paid = fields.Many2one('hr.payslip', string='Payslip of advance paid earlier')

    amount_bonus = fields.Float(string='Bonus Amount', compute='_get_allwns_expnse', readonly=True)
    amount_pd_leave = fields.Float(string='Paid Leave', compute='_get_allwns_expnse', store=True)
    amount_exp_leave = fields.Float(string='Leave Expense', compute='_get_allwns_expnse', store=True)
    amount_penalty = fields.Float(string='Penalty', compute='_get_allwns_expnse', store=True)

    @api.depends('line_ids')
    def _get_allwns_expnse(self):
        for rec in self:
            
            bonus1 = self.env['hr.bonus.request'].search([
                            ('employee_id','=',rec.employee_id.id),
                            ('date_from','=',rec.date_from),
                            ('date_to','=',rec.date_to),
                            ('multi_employee','=',False),
                            ('state','=','approve'),                            
                            ])
            bonus2 = self.env['hr.bonus.request'].search([
                            ('date_from','=',rec.date_from),
                            ('date_to','=',rec.date_to),
                            ('multi_employee','=',True),
                            ('state','=','approve'),                            
                            ])
            if bonus1:
                rec.amount_bonus = bonus1.amount
            elif bonus2:
                bonus = bonus2.filtered(lambda r: rec.employee_id.id in r.employee_ids.ids)
                bonus.ensure_one()
                rec.amount_bonus = bonus.amount

            leave = self.env['hr.leave.paid'].search([
                        ('employee_id','=',rec.employee_id.id),
                        ('date_from','=',rec.date_from),
                        ('date_to','=',rec.date_to),
                        ('state','=','approve'),
                        ])            
            rec.amount_pd_leave = leave.amount   

            leave = self.env['hr.leave.expense'].search([
                        ('employee_id','=',rec.employee_id.id),
                        ('date_from','=',rec.date_from),
                        ('date_to','=',rec.date_to),
                        ('state','=','approve'),
                        ])            
            rec.amount_exp_leave = leave.amount

            penalty = self.env['hr.pay.penalty'].search([
                        ('employee_id','=',rec.employee_id.id),
                        ('date_from','=',rec.date_from),
                        ('date_to','=',rec.date_to),
                        ('state','=','approve'),
                        ])            
            rec.amount_penalty = penalty.amount

    @api.depends('line_ids')
    def get_payslip_total(self):
        for r in self:
            result = r.line_ids.filtered(lambda r: r.code == 'NET').amount
            r.amount_payslip_total = result
        return result


    @api.v7
    def compute_sheet(self, cr, uid, ids, context=None):
        slip_line_pool = self.pool.get('hr.payslip.line')
        sequence_obj = self.pool.get('ir.sequence')
        for payslip in self.browse(cr, uid, ids, context=context):
            number = payslip.number or sequence_obj.next_by_code(cr, uid, 'salary.slip')
            #delete old payslip lines
            old_slipline_ids = slip_line_pool.search(cr, uid, [('slip_id', '=', payslip.id)], context=context)
#            old_slipline_ids
            if old_slipline_ids:
                slip_line_pool.unlink(cr, uid, old_slipline_ids, context=context)
            if payslip.contract_id:
                #set the list of contract for which the rules have to be applied
                contract_ids = [payslip.contract_id.id]
            else:
                #if we don't give the contract, then the rules to apply should be for all current contracts of the employee
                contract_ids = self.get_contract(cr, uid, payslip.employee_id, payslip.date_from, payslip.date_to, context=context)


            lines = [(0,0,line) for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context)]
            self.write(cr, uid, [payslip.id], {'line_ids': lines, 'number': number}, context=context)
        return True

class HrBonusRequest(models.Model):

    _name = 'hr.bonus.request'

    name = fields.Char(string='Reference')
    date_from = fields.Date('Date from')
    date_to = fields.Date('Date to')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    months = fields.Float('Number of Months')
    amount_month = fields.Float('Amount per Month(basic wage)')
    amount = fields.Float('Total Amount')
    state = fields.Selection([('draft','Draft'), ('reject', 'Rejected'), ('approve', 'Approved')],
                             default='draft')
    note = fields.Char('Note..')
    multi_employee = fields.Boolean('Apply for Multiple Employees', default=False)
    employee_ids = fields.Many2many('hr.employee', string='Employees')


    @api.onchange('employee_id')
    def get_basic_wage(self):
        result = False
        if self:
            self.amount_month = self.employee_id.contract_id.wage

    # @api.depends('months', 'amount_month')
    # def _get_amount_total(self):
    #     for r in self:
    #         r.amount = r.amount_month * r.months

    @api.onchange('months', 'amount_month')
    def _get_amount_total(self):
        if self.months and self.amount_month:
            self.amount = self.months * self.amount_month

    @api.onchange('date_to', 'date_from', 'employee_id', 'employee_ids', 'multi_employee')
    def _get_reference_name(self):
        if self.date_to and self.date_from:
            if self.multi_employee:
                self.name = 'BNS: MULTI/{}'.format(tools.ustr(ttyme.strftime('%B-%Y')))
                return True      
            elif self.employee_id:          
                ttyme = datetime.fromtimestamp(time.mktime(time.strptime(self.date_from, "%Y-%m-%d")))
                self.name = 'BNS: {}/{}'.format(self.employee_id.name, tools.ustr(ttyme.strftime('%B-%Y')))

    @api.multi
    def make_bonus_approved(self):
        self.prevent_multiple_bonuses()
        self.state = 'approve'

    @api.multi
    def make_bonus_rejected(self):
        self.state = 'reject'


    @api.constrains('employee_id', 'date_from', 'date_to')
    def prevent_multiple_bonuses(self):
        bonuses = self.search([
                        ('id', '!=', self.id),
                        ('employee_id','=',self.employee_id.id),
                        ('multi_employee','=',False),
                        ('date_from','=',self.date_from),
                        ('date_to','=',self.date_to),
                        ('state','=','approve'),])
        if bonuses:
            raise ValidationError("You have already made a bonus for this period for this employee, can't create new one")
        bonuses = self.search([
                        ('id', '!=', self.id),
                        ('multi_employee','=',True),
                        ('date_from','=',self.date_from),
                        ('date_to','=',self.date_to),
                        ('state','=','approve'),])
        if bonuses.filtered(lambda r: self.employee_id.id in r.employee_ids.ids):
            raise ValidationError("You have already made a bonus for this period for this employee, can't create new one")


class HrPaidLeave(models.Model):

    _name = 'hr.leave.paid'

    name = fields.Char(string='Reference')
    date_from = fields.Date('Date from')
    date_to = fields.Date('Date to')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    amount_day = fields.Float('Amount per Day')
    days = fields.Float('Number of Days')
    amount = fields.Float('Total Credit', compute='_get_amount_total')
    state = fields.Selection([('draft','Draft'), ('reject', 'Rejected'), ('approve', 'Approved')],
                             default='draft')
    note = fields.Text('Note..')

    @api.depends('days', 'amount_day')
    def _get_amount_total(self):
        for r in self:
            r.amount = r.amount_day * r.days

    @api.onchange('date_to', 'date_from', 'employee_id')
    def _get_reference_name(self):
        if self.date_to and self.date_from and self.employee_id:
            ttyme = datetime.fromtimestamp(time.mktime(time.strptime(self.date_from, "%Y-%m-%d")))
            self.name = 'PD-LV: {}/{}'.format(self.employee_id.name, tools.ustr(ttyme.strftime('%B-%Y')))

    @api.multi
    def make_pd_leave_approved(self):
        self.state = 'approve'

    @api.multi
    def make_pd_leave_rejected(self):
        self.state = 'reject'


    @api.constrains('employee_id', 'date_from', 'date_to')
    def prevent_multiple_lv_records(self):
        leaves = self.search([
                        ('id', '!=', self.id),
                        ('employee_id','=',self.employee_id.id),
                        ('date_from','=',self.date_from),
                        ('date_to','=',self.date_to),
                        ('state','=','approve'),])
        if leaves:
            raise ValidationError("You have already made a Paid Leave request for this period, can't create new one")

class HrExpenseLeave(models.Model):

    _name = 'hr.leave.expense'

    name = fields.Char(string='Reference')
    date_from = fields.Date('Date from')
    date_to = fields.Date('Date to')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    amount = fields.Float('Total Amount')
    state = fields.Selection([('draft','Draft'), ('reject', 'Rejected'), ('approve', 'Approved')],
                             default='draft')
    note = fields.Text('Note..')


    @api.onchange('date_to', 'date_from', 'employee_id')
    def _get_reference_name(self):
        if self.date_to and self.date_from and self.employee_id:
            ttyme = datetime.fromtimestamp(time.mktime(time.strptime(self.date_from, "%Y-%m-%d")))
            self.name = 'EXP-LV: {}/{}'.format(self.employee_id.name, tools.ustr(ttyme.strftime('%B-%Y')))

    @api.multi
    def make_exp_leave_approved(self):
        self.state = 'approve'

    @api.multi
    def make_exp_leave_rejected(self):
        self.state = 'reject'


    @api.constrains('employee_id', 'date_from', 'date_to')
    def prevent_multiple_lv_records(self):
        leaves = self.search([
                        ('id', '!=', self.id),
                        ('employee_id','=',self.employee_id.id),
                        ('date_from','=',self.date_from),
                        ('date_to','=',self.date_to),
                        ('state','=','approve'),])
        if leaves:
            raise ValidationError("You have already made a Leave Expense request for this period, can't create new one")

class HrExpenseLeave(models.Model):

    _name = 'hr.pay.penalty'

    name = fields.Char(string='Reference')
    date_from = fields.Date('Date from')
    date_to = fields.Date('Date to')
    employee_id = fields.Many2one('hr.employee', string='Employee')

    amount = fields.Float('Total Amount')
    state = fields.Selection([('draft','Draft'), ('reject', 'Rejected'), ('approve', 'Approved')],
                             default='draft')
    note = fields.Text('Note..')


    @api.onchange('date_to', 'date_from', 'employee_id')
    def _get_reference_name(self):
        if self.date_to and self.date_from and self.employee_id:
            ttyme = datetime.fromtimestamp(time.mktime(time.strptime(self.date_from, "%Y-%m-%d")))
            self.name = 'PENALTY: {}/{}'.format(self.employee_id.name, tools.ustr(ttyme.strftime('%B-%Y')))

    @api.multi
    def make_penalty_approved(self):
        self.state = 'approve'

    @api.multi
    def make_penalty_rejected(self):
        self.state = 'reject'


    @api.constrains('employee_id', 'date_from', 'date_to')
    def prevent_multiple_lv_records(self):
        leaves = self.search([
                        ('id', '!=', self.id),
                        ('employee_id','=',self.employee_id.id),
                        ('date_from','=',self.date_from),
                        ('date_to','=',self.date_to),
                        ('state','=','approve'),])
        if leaves:
            raise ValidationError("You have already made a Leave Expense request for this period, can't create new one")
