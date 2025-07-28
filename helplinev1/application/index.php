<html>
<head>
<meta charset=UTF-8>
<title>Helpline</title>
<script>
<?php
include "config.php";
 
echo "var VA_SIP_USER_PREFIX = \"".$VA_SIP_USER_PREFIX."\";\r\n";
echo "var VA_SIP_PASS_PREFIX = \"".$VA_SIP_PASS_PREFIX."\";\r\n";
echo "var VA_SIP_HOST = \"".$VA_SIP_HOST."\";\r\n";
echo "var VA_ICE_HOST = \"".$VA_ICE_HOST."\";\r\n";
echo "var VA_AMI_HOST = \"".$VA_AMI_HOST."\";\r\n";
echo "var VA_ATI_HOST = \"".$VA_ATI_HOST."\";\r\n";

echo "var APP_LOGO = \"".$APP_LOGO."\";\r\n";
echo "var COUNTRY_CODE = \"".$COUNTRY_CODE."\";\r\n";
echo "var CASE_ID_PREFIX = \"".$CASE_ID_PREFIX."\";\r\n";

// --- CATEGORY ROOT IDs ---

echo "var CASE_CATEGORY_ROOT_ID = \"".$CASE_CATEGORY_ROOT_ID."\";\r\n";
echo "var CASE_ASSESSMENT_ROOT_ID = \"".$CASE_ASSESSMENT_ROOT_ID."\";\r\n";
echo "var CASE_JUSTICE_ROOT_ID = \"".$CASE_JUSTICE_ROOT_ID."\";\r\n";
echo "var CASE_REFERALS_ROOT_ID = \"".$CASE_REFERALS_ROOT_ID."\";\r\n";
echo "var CASE_SERVICES_ROOT_ID = \"".$CASE_SERVICES_ROOT_ID."\";\r\n";
echo "var CASE_KNOW_ABOUT_116_ROOT_ID = \"".$CASE_KNOW_ABOUT_116_ROOT_ID."\";\r\n";

echo "var AGE_GROUP_ROOT_ID = \"".$AGE_GROUP_ROOT_ID."\";\r\n";
echo "var SEX_ROOT_ID = \"".$SEX_ROOT_ID."\";\r\n";
echo "var LOCATION_ROOT_ID = \"".$LOCATION_ROOT_ID."\";\r\n";
echo "var NATIONALITY_ROOT_ID = \"".$NATIONALITY_ROOT_ID."\";\r\n";
echo "var NATIONAL_ID_TYPE_ROOT_ID = \"".$NATIONAL_ID_TYPE_ROOT_ID."\";\r\n";
echo "var LANGUAGE_ROOT_ID = \"".$LANGUAGE_ROOT_ID."\";\r\n";
echo "var TRIBE_ROOT_ID = \"".$TRIBE_ROOT_ID."\";\r\n";

echo "var RELATIONSHIP_ROOT_ID = \"".$RELATIONSHIP_ROOT_ID."\";\r\n";
echo "var HEALTH_STATUS_ROOT_ID = \"".$HEALTH_STATUS_ROOT_ID."\";\r\n";
echo "var HIV_STATUS_ROOT_ID = \"".$HIV_STATUS_ROOT_ID."\";\r\n";
echo "var MARITAL_STATUS_ROOT_ID = \"".$MARITAL_STATUS_ROOT_ID."\";\r\n";
echo "var EMPLOYMENT_STATUS_ROOT_ID = \"".$EMPLOYMENT_STATUS_ROOT_ID."\";\r\n";
echo "var HOUSEHOLD_TYPE_ROOT_ID = \"".$HOUSEHOLD_TYPE_ROOT_ID."\";\r\n";
echo "var SHARES_HOME_ROOT_ID = \"".$SHARES_HOME_ROOT_ID."\";\r\n";
echo "var NOT_IN_SCHOOL_ROOT_ID = \"".$NOT_IN_SCHOOL_ROOT_ID."\";\r\n";
echo "var SCHOOL_TYPE_ROOT_ID = \"".$SCHOOL_TYPE_ROOT_ID."\";\r\n";
echo "var SCHOOL_LEVEL_ROOT_ID = \"".$SCHOOL_LEVEL_ROOT_ID."\";\r\n";
echo "var DISABILITY_ROOT_ID = \"".$DISABILITY_ROOT_ID."\";\r\n";

echo "var DISPOSITION_ROOT_ID = \"".$DISPOSITION_ROOT_ID."\";\r\n";

// --- CATEGORY IDs ---

echo "var CASE_CATEGORY_ABUSE_ID = \"".$CASE_CATEGORY_ABUSE_ID."\";\r\n";
echo "var CASE_CATEGORY_SEXUAL_ABUSE_ID = \"".$CASE_CATEGORY_SEXUAL_ABUSE_ID."\";\r\n";
echo "var CASE_CATEGORY_PHYSICAL_N_SEXUAL_ABUSE_ID = \"".$CASE_CATEGORY_PHYSICAL_N_SEXUAL_ABUSE_ID."\";\r\n";
echo "var CASE_SERVICE_REFERAL_ID = \"".$CASE_SERVICE_REFERAL_ID."\";\r\n";
echo "var CASE_SERVICE_POLICE_ID = \"".$CASE_SERVICE_POLICE_ID."\";\r\n";
echo "var CASE_SERVICE_OTHER_ID = \"".$CASE_SERVICE_OTHER_ID."\";\r\n";
echo "var CASE_REFERAL_OTHER_ID = \"".$CASE_REFERAL_OTHER_ID."\";\r\n";

echo "var MARITAL_STATUS_WITH_SPOUSE_ID = \"".$MARITAL_STATUS_WITH_SPOUSE_ID."\";\r\n";

echo "var DISPOSITION_ID_DEFAULT = \"".$DISPOSITION_ID_DEFAULT."\";\r\n";
echo "var DISPOSITION_ID_COMPLETE = \"".$DISPOSITION_ID_COMPLETE."\";\r\n";
echo "var DISPOSITION_ID_NEW_CASE = \"".$DISPOSITION_ID_NEW_CASE."\";\r\n";
echo "var DISPOSITION_ID_FOLLOWUP = \"".$DISPOSITION_ID_FOLLOWUP."\";\r\n";
echo "var DISPOSITION_ID_EDIT = \"".$DISPOSITION_ID_EDIT."\";\r\n";
echo "var DISPOSITION_ID_CONTACT_NEW = \"".$DISPOSITION_ID_CONTACT_NEW."\";\r\n";
echo "var DISPOSITION_ID_CONTACT_EDIT = \"".$DISPOSITION_ID_CONTACT_EDIT."\";\r\n";
echo "var DISPOSITION_ID_CASE_UPDATE = \"".$DISPOSITION_ID_CASE_UPDATE."\";\r\n";
echo "var DISPOSITION_ID_CASE_UPDATE_FOLLOWUP = \"".$DISPOSITION_ID_CASE_UPDATE_FOLLOWUP."\";\r\n";
echo "var DISPOSITION_ID_CASE_EDIT = \"".$DISPOSITION_ID_CASE_EDIT."\";\r\n";
echo "var DISPOSITION_ID_CASE_EDIT_FOLLOWUP = \"".$DISPOSITION_ID_CASE_EDIT_FOLLOWUP."\";\r\n";

echo "\r\nrz[\"location\"]=[".$LOCATION_HIERARCHY."];\r\n";
?>
</script>

<!-- External SIP Library -->
<script src="/helpline/js/sip-0.20.0.js"></script>

<!-- Core JavaScript Libraries -->
<script src="/helpline/js/te.js"></script>
<script src="/helpline/js/sel.js"></script>
<script src="/helpline/js/chk.js"></script>
<script src="/helpline/js/enum.js"></script>
<script src="/helpline/js/cal.js"></script>
<script src="/helpline/js/tf.js"></script>
<script src="/helpline/js/rpt.js"></script>
<script src="/helpline/js/xlsx.js"></script>
<script src="/helpline/js/chart.js"></script>

<!-- Application JavaScript Modules -->
<script src="/helpline/app/user.js"></script>
<script src="/helpline/app/contact.js"></script>
<script src="/helpline/app/phone.js"></script>
<script src="/helpline/app/cti.js"></script>
<script src="/helpline/app/ati.js"></script>
<script src="/helpline/app/call.js"></script>
<script src="/helpline/app/msg.js"></script>
<script src="/helpline/app/schedule.js"></script>
<script src="/helpline/app/category.js"></script>
<script src="/helpline/app/activity.js"></script>
<script src="/helpline/app/disposition.js"></script>
<script src="/helpline/app/qa.js"></script>
<script src="/helpline/app/reporter.js"></script>
<script src="/helpline/app/client.js"></script>
<script src="/helpline/app/perp.js"></script>
<script src="/helpline/app/attachment.js"></script>
<script src="/helpline/app/case.js"></script>
<script src="/helpline/app/case_activity.js"></script>
<script src="/helpline/app/safepal.js"></script>
<script src="/helpline/app/aii.js"></script>
<script src="/helpline/app/app.js"></script>

</head>
<body id="vdd" style="height:100%;" onclick='undd(this);' >
<?php
echo "
<style>
";
include "screen.css";
echo "
</style>
";
?>
<div oncontextmenu=""><div id='vv'></div></div>
<div class='g' id='lds'></div>
</body>
</html>