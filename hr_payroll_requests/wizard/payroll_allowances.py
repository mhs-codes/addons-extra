from openerp import models,fields,api

class BonusReportWizard(models.TransientModel):

    _name = 'bonus.report'

 
    all_department = fields.Boolean('All Departments')
    department_id = fields.Many2one('hr.department','Department ID')


    @api.multi
    def print_report(self):

        report_obj = self.env['report']
        return {

            'type': 'ir.actions.report.xml',
            'report_name': 'hr_payroll_requests.report_bonus_template',
            



        }

class PaidLeaveReportWizard(models.TransientModel):

    _name = 'paid.leave'

 
    all_department = fields.Boolean('All Departments')
    department_id = fields.Many2one('hr.department','Department ID')


    @api.multi
    def print_report(self):

        report_obj = self.env['report']
        return {

            'type': 'ir.actions.report.xml',
            'report_name': 'hr_payroll_requests.paid_leave_template',
            



        }

class LeaveExpenseReportWizard(models.TransientModel):

    _name = 'leave.expense'

 
    all_department = fields.Boolean('All Departments')
    department_id = fields.Many2one('hr.department','Department ID')


    @api.multi
    def print_report(self):

        report_obj = self.env['report']
        return {

            'type': 'ir.actions.report.xml',
            'report_name': 'hr_payroll_requests.leave_expense_template',
      
        }

    