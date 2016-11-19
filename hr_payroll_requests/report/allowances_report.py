from openerp import models,fields,api

class BonusReportParser(models.AbstractModel):
    _name = 'report.hr_payroll_requests.report_bonus_template'


    @api.multi
    def get_total(self,docs):
        if docs:
            
            vals = {

                'net' : sum([doc.net_amount for doc in docs]),
                'gross' : sum([doc.gross_amount for doc in docs]),
                'bonus' : sum([doc.amount_bonus for doc in docs]),

            }

            return vals
        else:
            return False


    
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        payslip_obj = self.env['hr.payslip']
        bonus_obj = self.env['bonus.report'].browse(self.ids)

        if bonus_obj.department_id:
            docs = payslip_obj.search([]).filtered(lambda r: r.employee_id.department_id.id==bonus_obj.department_id.id)
        else:
            docs = payslip_obj.search([])

        bonus_slips = []
        for doc in docs:
            for line in doc.line_ids:
                if line.code=='BONUS':
                    bonus_slips.append(doc.id)

        bonus_docs = payslip_obj.browse(bonus_slips)

        docargs = {
            'docs': bonus_docs,
            'get_totals': self.get_total(bonus_docs),
        }
        
        
        return report_obj.render('hr_payroll_requests.report_bonus_template',docargs)

class PaidLeaveParser(models.AbstractModel):
    _name = 'report.hr_payroll_requests.paid_leave_template'

    @api.multi
    def get_total(self,docs):
        if docs:
            
            vals = {

                'net' : sum([doc.net_amount for doc in docs]),
                'gross' : sum([doc.gross_amount for doc in docs]),
                'bonus' : sum([doc.amount_pd_leave for doc in docs]),

            }

            return vals
        else:
            return False
    
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        payslip_obj = self.env['hr.payslip']
        bonus_obj = self.env['paid.leave'].browse(self.ids)

        if bonus_obj.department_id:
            docs = payslip_obj.search([]).filtered(lambda r: r.employee_id.department_id.id==bonus_obj.department_id.id)
        else:
            docs = payslip_obj.search([])

        paid_leave_slips = []
        for doc in docs:
            for line in doc.line_ids:
                if line.code=='PDLEAVE':
                    paid_leave_slips.append(doc.id)

        paid_docs = payslip_obj.browse(paid_leave_slips)

        docargs = {
            'docs': paid_docs,
            'get_totals': self.get_total(paid_docs),

        }
        
        
        return report_obj.render('hr_payroll_requests.paid_leave_template',docargs)

class LeaveExpenseParser(models.AbstractModel):
    _name = 'report.hr_payroll_requests.leave_expense_template'

    @api.multi
    def get_total(self,docs):
        if docs:
            
            vals = {

                'net' : sum([doc.net_amount for doc in docs]),
                'gross' : sum([doc.gross_amount for doc in docs]),
                'bonus' : sum([doc.amount_exp_leave for doc in docs]),

            }

            return vals
        else:
            return False
    
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        payslip_obj = self.env['hr.payslip']
        bonus_obj = self.env['leave.expense'].browse(self.ids)

        if bonus_obj.department_id:
            docs = payslip_obj.search([]).filtered(lambda r: r.employee_id.department_id.id==bonus_obj.department_id.id)
        else:
            docs = payslip_obj.search([])

        leave_expense_slips = []
        for doc in docs:
            for line in doc.line_ids:
                if line.code=='EXPLEAVE':
                    leave_expense_slips.append(doc.id)

        leave_expense_docs = payslip_obj.browse(leave_expense_slips)

        docargs = {
            'docs': leave_expense_docs,
            'get_totals': self.get_total(leave_expense_docs),
            
        }
        
        
        return report_obj.render('hr_payroll_requests.leave_expense_template',docargs)


