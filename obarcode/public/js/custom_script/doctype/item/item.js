frappe.ui.form.on("Item", "refresh", function(frm) {
    frm.add_custom_button(__("Create Barcode"), function() {
        // frappe.route_options = {
        //     "item_code": frm.doc.name
        // }
        // frappe.set_route("query-report", "Stock Balance");
        reject_items({frm: me.frm});
    });
});


let reject_items = (opts) => {
	const frm = opts.frm;
	const dialog = new frappe.ui.Dialog({
		title: __('Please provide reason for rejection'),
		fields: [
			{
				fieldtype: 'Small Text', fieldname: 'approver_comment', label: __('Comment'),
				reqd: 1,
			}
		],
		primary_action: () => {
			dialog.hide();
			let vals = dialog.get_values();
			if (!vals) return;
			frappe.call({
                method: "obarcode.utils.generate_item_barcode",
                args: {
                    doc: frm.doc
                },
                freeze: true,
                callback: function(r) {
                    let message = frm.doc.disabled ? "Dimension Disabled" : "Dimension Enabled";
                    frm.save();
                    frappe.show_alert({message:__(message), indicator:'green'});
                }
            });
			
		},
		primary_action_label: __('Reject')
	});
	dialog.show();
}