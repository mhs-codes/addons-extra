odoo.define('mhs_test.script01', function(require) {
	"use strict";

// var base = require('web_editor.base');
var core = require('web.core');
// var ajax = require('web.ajax');
var common = require('web.form_common');
var ListView = require('web.ListView');
var data = require('web.data');
var qweb = core.qweb;
var _t = core._t;
var M2mCheck = core.form_widget_registry.get('many2many_checkboxes');
var M2m = core.form_widget_registry.get('many2many');

var M2mCheckMhsCustom = M2mCheck.extend({
	init: function(field_manager, node) {
        this._super.apply(this, arguments);
    },
    initialize_field: function() {
        common.ReinitializeFieldMixin.initialize_field.call(this);
        this.on("change:domain", this, this.query_records);
        this.set("domain", new data.CompoundDomain(this.build_domain()).eval());
        this.on("change:records", this, this.render_value);
        // debugger;
    },
    render_value: function() {
    	// debugger;
        this.$().html(qweb.render("TreeViewCustomMhs", {widget: this}));
        var inputs = this.$("input");
        inputs.change(_.bind(this.from_dom, this));
        if (this.get("effective_readonly"))
            inputs.attr("disabled", "true");
        // console.log(this);
    },

});

// -----------------------LIST----------------
var X2ManyListView = ListView.extend({
    is_valid: function () {
        var self = this;
        if (!this.fields_view || !this.editable()){
            return true;
        }
        if (_.isEmpty(this.records.records)){
            return true;
        }
        var fields = this.editor.form.fields;
        var current_values = {};
        _.each(fields, function(field){
            field._inhibit_on_change_flag = true;
            field.__no_rerender = field.no_rerender;
            field.no_rerender = true;
            current_values[field.name] = field.get('value');
        });
        var cached_records = _.filter(this.dataset.cache, function(item){return !_.isEmpty(item.values)});
        var valid = _.every(cached_records, function(record){
            _.each(fields, function(field){
                var value = record.values[field.name];
                field._inhibit_on_change_flag = true;
                field.no_rerender = true;
                field.set_value(_.isArray(value) && _.isArray(value[0]) ? [COMMANDS.delete_all()].concat(value) : value);
            });
            return _.every(fields, function(field){
                field.process_modifiers();
                field._check_css_flags();
                return field.is_valid();
            });
        });
        _.each(fields, function(field){
            field.set('value', current_values[field.name], {silent: true});
            field._inhibit_on_change_flag = false;
            field.no_rerender = field.__no_rerender;
        });
        return valid;
    },
});

var X2ManyList = ListView.List.extend({
    pad_table_to: function (count) {
        if (!this.view.is_action_enabled('create') || this.view.x2m.get('effective_readonly')) {
            this._super(count);
            return;
        }

        this._super(count > 0 ? count - 1 : 0);

        var self = this;
        var columns = _(this.columns).filter(function (column) {
            return column.invisible !== '1';
        }).length;
        if (this.options.selectable) { columns++; }
        if (this.options.deletable) { columns++; }

        var $cell = $('<td>', {
            colspan: columns,
            'class': 'oe_form_field_x2many_list_row_add'
        }).append(
            $('<a>', {href: '#'}).text(_t("Add an item"))
                .click(function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    // FIXME: there should also be an API for that one
                    if (self.view.editor.form.__blur_timeout) {
                        clearTimeout(self.view.editor.form.__blur_timeout);
                        self.view.editor.form.__blur_timeout = false;
                    }
                    self.view.save_edition().done(function () {
                        self.view.do_add_record();
                    });
                }));

        var $padding = this.$current.find('tr:not([data-id]):first');
        var $newrow = $('<tr>').append($cell);
        if ($padding.length) {
            $padding.before($newrow);
        } else {
            this.$current.append($newrow);
        }
    },
});

// ---------------MHS LIST BEGIN
var M2MListViewMhs = X2ManyListView.extend(/** @lends instance.web.form.Many2ManyListView# */{
    init: function (parent, dataset, view_id, options) {
        this._super(parent, dataset, view_id, _.extend(options || {}, {
            ListType: X2ManyList,
        }));
    },
    do_add_record: function () {
        var self = this;

        new common.SelectCreateDialog(this, {
            res_model: this.model,
            domain: new data.CompoundDomain(this.x2m.build_domain(), ["!", ["id", "in", this.x2m.dataset.ids]]),
            context: this.x2m.build_context(),
            title: _t("Add: ") + this.x2m.string,
            alternative_form_view: this.x2m.field.views ? this.x2m.field.views.form : undefined,
            no_create: this.x2m.options.no_create,
            on_selected: function(element_ids) {
                return self.x2m.data_link_multi(element_ids).then(function() {
                    self.x2m.reload_current_view();
                });
            }
        }).open();
    },
    do_activate_record: function(index, id) {
        var self = this;
        var pop = new common.FormViewDialog(this, {
            res_model: this.dataset.model, 
            res_id: id,
            context: this.x2m.build_context(),
            title: _t("Open: ") + this.x2m.string,
            alternative_form_view: this.x2m.field.views ? this.x2m.field.views.form : undefined,
            readonly: !this.is_action_enabled('edit') || self.x2m.get("effective_readonly"),
        }).open();
        pop.on('write_completed', self, function () {
            self.dataset.evict_record(id);
            self.reload_content();
        });
    },
    do_button_action: function(name, id, callback) {
        var self = this;
        var _sup = _.bind(this._super, this);
        if (! this.x2m.options.reload_on_button) {
            return _sup(name, id, callback);
        } else {
            return this.x2m.view.save().then(function() {
                return _sup(name, id, function() {
                    self.x2m.view.reload();
                });
            });
        }
    },
    load_list: function(data){
    	this._super(data);
    	console.log(data);
    }
});
// ------------------------------------LIST END-------------

var M2mMhsCustom = M2m.extend({
	multi_selection: true,
    init: function() {
        this._super.apply(this, arguments);
        this.x2many_views = {
            list: M2MListViewMhs,
            kanban: core.view_registry.get('many2many_kanban'),
        };
        // debugger;
    },
});

core.form_widget_registry
    .add('m2m_check_mhs', M2mCheckMhsCustom)
    .add('m2m_tree_check_mhs', M2mMhsCustom);

});