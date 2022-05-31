frappe.ui.form.on("Item", "refresh", function(frm) {
    frm.add_custom_button(__("Create Barcode"), function() {
        // frappe.route_options = {
        //     "item_code": frm.doc.name
        // }
        // frappe.set_route("query-report", "Stock Balance");
        
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Item Barcode",
                filters: [
                    ["parent", "=", frm.doc.name]
                ],
                fields: ["barcode"],
                parent: "Item"
            },
            callback: function(r) {
                reject_items({frm: me.frm,barcode: r.message});
            }
        });
    });
});


let reject_items = (opts) => {
    console.log(frappe.get_meta("Item Barcode"));
	const frm = opts.frm;
	const _barcode = opts.barcode;
    let barcode = [];
    console.log(_barcode);
    _barcode.forEach(element => {
        barcode.push(element.barcode);
    });
    console.log(barcode);


	const dialog = new frappe.ui.Dialog({
		title: __('Generate Barcode'),
		fields: [
			{
				fieldtype: 'Int', fieldname: 'qty', label: __('Qty'),
				reqd: 1,
                default : 1
			},
            {
                fieldtype:'Select', fieldname:'item_barcode', label:__('Barcode'),
			    options: Object.values(barcode),
                'reqd': 1
			    
		    },
            
            {
                fieldtype:'Select', fieldname:'label_size', label:__('Size'),
			    options: ['38mm x 25mm', '50mm x 25mm'].join('\n'),
                default : '50mm x 25mm'
            },
		],
		primary_action: () => {
			dialog.hide();
			let vals = dialog.get_values();
			if (!vals) return;
            let xLabel = 50.00;
            let yLabel = 25.00;
            if(vals.label_size == '38mm x 25mm'){
                xLabel = 38.00;
                yLabel = 25.00;
            }else if(vals.label_size == '50mm x 25mm'){
                xLabel = 50.00;
                yLabel = 25.00;
            }
			frappe.call({
                method: "obarcode.utils.generate_item_barcode",
                args: {
                    dt: frm.doc.doctype,
                    dn: frm.doc.name,
                    item_name: frm.doc.item_name,
                    item_rate: '',
                    item_barcode: vals.item_barcode,
                    qty: vals.qty,
                    x: xLabel,
                    y: yLabel,
                },
                freeze: true,
                callback: function(r) {
                    frm.reload_doc();
                    // frm.refresh();
                }
            });
			
		},
		primary_action_label: __('Generate')
	});
	dialog.show();
}