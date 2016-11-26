odoo.define('hr_payroll_requests.o2m_test', function (require) {
'use strict';

var core = require('web.core');
var data = require('web.data');
var common = require('web.form_common');
var RelFields = require('web.form_relational');

var QWeb = core.qweb;

var O2mTest = FieldOne2Many.extend({
    init: function() {
        this._super.apply(this, arguments);
    },
})

core.form_widget_registry
    .add('o2m_test', O2mTest)

});