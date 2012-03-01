# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
import pooler
from tools.translate import _

MODULE_LIST = [
               'analytic_user_function', 'analytic_journal_billing_rate', 'import_sugarcrm',
               'import_google', 'crm_caldav', 'wiki_sale_faq', 'base_contact','sale_layout','warning',
               'google_map', 'fetchmail_crm', 'plugin_thunderbird', 'plugin_outlook','account_analytic_analysis',
               'project_timesheet', 'account_analytic_analysis', 'project_mrp', 'delivery',
               'sale_margin', 'sale_journal'
]

class sale_configuration(osv.osv_memory):
    _inherit = 'res.config'

    _columns = {
        'sale_orders': fields.boolean('Based on Sales Orders',),
        'deli_orders': fields.boolean('Based on Delivery Orders'),
        'task_work': fields.boolean('Based on Tasks\' Work'),
        'timesheet': fields.boolean('Based on Timesheet'),
        'order_policy': fields.selection([
            ('manual', 'Invoice Based on Sales Orders'),
            ('picking', 'Invoice Based on Deliveries'),
        ], 'Main Method Based On', required=True, help="You can generate invoices based on sales orders or based on shippings."),
        'delivery': fields.boolean('Do you charge the delivery?'),
        'time_unit': fields.many2one('product.uom','Working Time Unit'),
        'picking_policy' : fields.boolean("Deliver all products at once?"),
        'group_sale_delivery_address':fields.boolean("Multiple Address",help="Group To Allow delivery address different from invoice address"),
        'group_sale_disc_per_sale_order_line':fields.boolean("Discounts per sale order lines ",help="Group to apply discounts per sale order lines"),
        'sale_layout':fields.boolean("Notes & subtotals per line",help="Install sale_layout module: This module provides features to improve the layout of the Sales Order.."),
        'warning': fields.boolean("Alerts by products or customers",
                                  help="Install warning module: Module to trigger warnings in OpenERP objects."),
        'sale_margin': fields.boolean("Display Margin For Users",
                        help="Install sale_margin module: This module adds the 'Margin' on sales order."),
        'sale_journal': fields.boolean("Invoice journal?",
                        help="Install sale_journal module: The sales journal modules allows you to categorise your sales and deliveries (picking lists) between different journals."),
        'analytic_user_function' : fields.boolean("User function by contracts",
                                    help="Install analytic_user_function module:This module allows you to define what is the default function of a specific user on a given account"),
        'analytic_journal_billing_rate' : fields.boolean("Billing rates by contracts",
                                    help="Install analytic_journal_billing_rate module: This module allows you to define what is the default invoicing rate for a specific journal on a given account."),
        'import_sugarcrm' : fields.boolean("Import data from sugarCRM?",
                                    help="Install import_sugarcrm module: This Module Import SugarCRM Leads, Opportunities, Users, Accounts, Contacts, Employees, Meetings, Phonecalls, Emails, and Project, Project Tasks Data into OpenERP Module."),
        'import_google' : fields.boolean("Import Contacts & Meetings from Google",
                                    help="Install import_google module: The module adds google contact in partner address and add google calendar events details in Meeting"),
        'wiki_sale_faq' : fields.boolean("Install a sales FAQ?",
                                    help="Install wiki_sale_faq module: This module provides a Wiki Sales FAQ Template."),
        'base_contact' : fields.boolean("Manage a several address per customer",
                                    help="Install crm_partner_assign module: This is the module used by OpenERP SA to redirect customers to its partners, based on geolocalization."),
        'google_map' : fields.boolean("Google maps on customer",
                                    help="Install google_map module: The module adds Google Map field in partner address."),
        'plugin_thunderbird': fields.boolean('Thunderbird plugin',
                                    help="Install plugin_thunderbird module: This module is required for the Thuderbird Plug-in to work properly."),
        'plugin_outlook': fields.boolean('Outlook plugin',
                                    help="Install plugin_outlook module: This module provides the Outlook Plug-in."),
        'account_analytic_analysis': fields.boolean('Contracts',
                                    help="Install account_analytic_analysis module: This module is for modifying account analytic view to show important data to project manager of services companies."),
    }

    def get_default_installed_modules(self, cr, uid, ids, context=None):
        installed_modules = {}
        if installed_modules.get('project_mrp') and installed_modules.get('project_timesheet'):
            installed_modules['task_work'] = True
        if installed_modules.get('account_analytic_analysis'):
            installed_modules['timesheet'] = True
        return installed_modules
    
    def get_default_sale_configs(self, cr, uid, ids, context=None):
        ir_values_obj = self.pool.get('ir.values')
        data_obj = self.pool.get('ir.model.data')
        menu_obj = self.pool.get('ir.ui.menu')
        result = {}
        invoicing_groups_id = [gid.id for gid in data_obj.get_object(cr, uid, 'sale', 'menu_invoicing_sales_order_lines').groups_id]
        picking_groups_id = [gid.id for gid in data_obj.get_object(cr, uid, 'sale', 'menu_action_picking_list_to_invoice').groups_id]
        group_id = data_obj.get_object(cr, uid, 'base', 'group_sale_salesman').id
        for menu in ir_values_obj.get(cr, uid, 'default', False, ['ir.ui.menu']):
            if menu[1] == 'groups_id' and group_id in menu[2][0]:
                if group_id in invoicing_groups_id:
                    result['sale_orders'] = True
                if group_id in picking_groups_id:
                    result['deli_orders'] = True
        for res in ir_values_obj.get(cr, uid, 'default', False, ['sale.order']):
            result[res[1]] = res[2]
        return result
    
    def default_get(self, cr, uid, fields_list, context=None):
        result = super(sale_configuration, self).default_get(
            cr, uid, fields_list, context=context)
        for method in dir(self):
            if method.startswith('get_default_'):
                result.update(getattr(self, method)(cr, uid, [], context))
        return result
    
    _defaults = {
        'order_policy': 'manual',
        'time_unit': lambda self, cr, uid, c: self.pool.get('product.uom').search(cr, uid, [('name', '=', _('Hour'))], context=c) and self.pool.get('product.uom').search(cr, uid, [('name', '=', _('Hour'))], context=c)[0] or False,
    }

    def create(self, cr, uid, vals, context=None):
        ids = super(sale_configuration, self).create(cr, uid, vals, context=context)
        self.execute(cr, uid, [ids], vals, context=context)
        return ids 
    
    def write(self, cr, uid, ids, vals, context=None):
        self.execute(cr, uid, ids, vals, context=context)
        return super(sale_configuration, self).write(cr, uid, ids, vals, context=context)

    def execute(self, cr, uid, ids, vals, context=None):
        #TODO: TO BE IMPLEMENTED
        for method in dir(self):
            if method.startswith('set_'):
                vals['modules'] = MODULE_LIST
                getattr(self, method)(cr, uid, ids, vals, context)
        return True

#    def set_installed_modules(self, cr, uid, ids, vals, context=None):
#        module_obj = self.pool.get('ir.module.module')
#        MODULE_LIST = vals.get('modules')
#        if vals.get('task_work'):
#            vals.update({'project_timesheet': True,'project_mrp': True})
#        if vals.get('timesheet'):
#            vals.update({'account_analytic_analysis': True})

    def set_sale_defaults(self, cr, uid, ids, vals, context=None):
        ir_values_obj = self.pool.get('ir.values')
        data_obj = self.pool.get('ir.model.data')
        menu_obj = self.pool.get('ir.ui.menu')
        res = {}
        wizard = self.browse(cr, uid, ids)[0]
        group_id = data_obj.get_object(cr, uid, 'base', 'group_sale_salesman').id

        if wizard.sale_orders:
            menu_id = data_obj.get_object(cr, uid, 'sale', 'menu_invoicing_sales_order_lines').id
            menu_obj.write(cr, uid, menu_id, {'groups_id':[(4,group_id)]})
            ir_values_obj.set(cr, uid, 'default', False, 'groups_id', ['ir.ui.menu'], [(4,group_id)])

        if wizard.deli_orders:
            menu_id = data_obj.get_object(cr, uid, 'sale', 'menu_action_picking_list_to_invoice').id
            menu_obj.write(cr, uid, menu_id, {'groups_id':[(4,group_id)]})
            ir_values_obj.set(cr, uid, 'default', False, 'groups_id', ['ir.ui.menu'], [(4,group_id)])
            
        if wizard.picking_policy:
            ir_values_obj.set(cr, uid, 'default', False, 'picking_policy', ['sale.order'], 'one')

        if wizard.time_unit:
            prod_id = data_obj.get_object(cr, uid, 'product', 'product_consultant').id
            product_obj = self.pool.get('product.product')
            product_obj.write(cr, uid, prod_id, {'uom_id': wizard.time_unit.id, 'uom_po_id': wizard.time_unit.id})

        ir_values_obj.set(cr, uid, 'default', False, 'order_policy', ['sale.order'], wizard.order_policy)
        if wizard.task_work and wizard.time_unit:
            company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
            self.pool.get('res.company').write(cr, uid, [company_id], {
                'project_time_mode_id': wizard.time_unit.id
            }, context=context)
            
        return res

    def onchange_tax_policy(self, cr, uid, ids, tax_policy, context=None):
        self.set_tax_policy(cr, uid, ids, {'tax_policy': tax_policy}, context=context)
        return {'value': {}}
    
    def set_default_taxes(self, cr, uid, ids, vals, context=None):
        ir_values_obj = self.pool.get('ir.values')
        taxes = self._check_default_tax(cr, uid, context=context)
        if isinstance(vals.get('tax_value'), list):
            taxes = vals.get('tax_value')
        if taxes:
            ir_values_obj.set(cr, uid, 'default', False, 'tax_id', ['sale.order'], taxes[0])
            ir_values_obj.set(cr, uid, 'default', False, 'tax_id', ['sale.order.line'], taxes)
            ir_values_obj.set(cr, uid, 'default', False, 'taxes_id', ['product.product'], taxes)

sale_configuration()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: