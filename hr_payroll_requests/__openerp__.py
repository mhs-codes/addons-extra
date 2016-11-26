{
   'name' : 'Allowances and Deduction Payments',
   'version' : '9.0.2.0',
   'author' : 'IDS ',
   'depends' : ['base','hr','hr_payroll', 'web'],
   'category' : 'General',
   'description' : """Salary Advance Payment """,
   'data' : [

            # 'security/service_security.xml',
            # 'security/ir.model.access.csv',
            'data.xml',
            'views/hr_views.xml',
            'views/allowance_reports.xml',
            # 'views/allowance_report_templates.xml',
            'report/report_actions.xml',



                 ],
}

