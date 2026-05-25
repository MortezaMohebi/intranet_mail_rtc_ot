# -*- coding: utf-8 -*-
{
    "name": "Intranet Mail RTC",
    "summary": "Make Odoo Discuss RTC safe for intranet and airgapped deployments.",
    "version": "18.0.1.0.6",
    "category": "Discuss",
    "author": "Odootech",
    "website": "https://odootech.ir",
    "license": "LGPL-3",
    "depends": ["mail", "bus", "web"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ir_config_parameter_data.xml",
        "views/res_config_settings_views.xml",
        "views/intranet_rtc_diagnostic_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            (
                "replace",
                "mail/static/src/discuss/call/common/rtc_service.js",
                "intranet_mail_rtc_ot/static/src/js/intranet_rtc_patch.js",
            ),
            (
                "replace",
                "mail/static/src/discuss/call/common/peer_to_peer.js",
                "intranet_mail_rtc_ot/static/src/js/peer_to_peer_patch.js",
            ),
            (
                "replace",
                "mail/static/src/discuss/call/common/blur_manager.js",
                "intranet_mail_rtc_ot/static/src/js/blur_manager_local.js",
            ),
            "intranet_mail_rtc_ot/static/src/xml/intranet_rtc_templates.xml",
        ],
        "web.qunit_suite_tests": [
            "intranet_mail_rtc_ot/static/tests/intranet_rtc_tests.js",
        ],
    },
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": False,
}
