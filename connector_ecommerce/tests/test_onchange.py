# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
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

import unittest2
import mock
import magento

from openerp.addons.connector.connector import ConnectorUnit
from openerp.addons.connector_ecommerce.unit.mapper import \
                                         SaleOrderImportMapper
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.connector import Environment
import openerp.tests.common as common

DB = common.DB
ADMIN_USER_ID = common.ADMIN_USER_ID


class test_onchange(common.TransactionCase):
    """ Test the imports from a Magento Mock """

    def setUp(self):
        super(test_onchange, self).setUp()
        self.session = ConnectorSession(self.cr, self.uid)

    def test_play_onchange(self):
        product_model = self.registry('product.product')
        partner_model = self.registry('res.partner')
        shop_model = self.registry('sale.shop')
        
        backend_record = mock.Mock()
        env = Environment(backend_record, self.session, 'sale.order')

        partner_id = partner_model.create(self.cr, self.uid, {
                'name': 'seb',
                'zip': '69100',
                'city': 'Villeurbanne',
                })
        
        partner_invoice_id = partner_model.create(self.cr, self.uid, {
                'name': 'Guewen',
                'zip': '1015',
                'city': 'Lausanne',
                'type': 'invoice',
                'parent_id': partner_id,
                })

        product_id = product_model.create(self.cr, self.uid, {
                'name': 'My Product',
                'weight': 15,
                })

        shop_id = shop_model.create(self.cr, self.uid, {
                'name': 'My shop',
                })

        order_input = {
            'shop_id': shop_id,
            'name': 'mag_10000001',
            'partner_id': partner_id,
            'order_line': [
                (0,0,{
                    'product_id': product_id,
                    'price_unit': 20,
                    'name': 'My Real Name',
                    'product_uom_qty': 1,
                }),
            ]
        }
 
        mapper = SaleOrderImportMapper(env)
        order = mapper._after_mapping(order_input)
        
        self.assertEqual(order['partner_invoice_id'], partner_invoice_id)
        line = order['order_line'][0][2] 
        self.assertEqual(line['name'], 'My Real Name')
        self.assertEqual(line['th_weight'], 15)

