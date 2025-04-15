
re["case_title"] =
{
"my_cases":["my_cases","My Cases"],
"esca_by_me":["esca_by_me","Escalated By Me"],
"esca_to_me":["esca_to_me","Escalated To Me"],
"all_cases":["all_cases","All Cases"],
"all_cases_today":["all_cases_today","All Cases Today"],
};

rk["case_metrics"] = ["case_count","case_percent"];
re["case_metrics"] = 
{
"case_count":	["case_count",	"Count","0","case_rpt_count","case_rpt-cases-@:1:0:0"],
"case_percent":	["case_percent",	"Percent","1","case_rpt_percent","case_rpt-cases-@:1:1:1"],
}; 

re["case_k"] = 
{
	"cat_0":["cat_0","Main Category"],
	"cat_1":["cat_1","SubCategory 1"],
	"cat_2":["cat_2","SubCategory 2"],
	"cat_3":["cat_3","SubCategory 3"],
        "cat_4":["cat_3","SubCategory 4"],
        "gbv_related":["gbv_related","GBV Related"],
	"src":["src","Case Source"],
	"priority":["priority","Priority"],
	"status":["status","Status"],
	"created_by":["created_by","Created By"],
	"escalated_to":["escalated_to","Escalated To"],
	"escalated_by":["escalated_by","Escalated By"],
	"assessment":["assessment","Case Assessment"],
	"justice":["justice","Status in the Justice System"],

	"reporter_age_group":["reporter_age_group","Reporter Age Group"],
	"reporter_sex":["reporter_sex","Reporter Sex"],
	"reporter_national_id_type":["reporter_national_id_type","Reporter ID Type"],
	"reporter_nationality":["reporter_nationality","Reporter Nationality"],
	"reporter_lang":["reporter_lang","Reporter Language"],
	"reporter_tribe":["reporter_tribe","Reporter Tribe"],

	"reporter_location_0":["reporter_location_0","Reporter Region"], //  region, district_2019, county_2019, subcounty_2019, parish_2019, lc1_2019, ec_constituency_201
	"reporter_location_1":["reporter_location_1","Reporter District"],
	"reporter_location_2":["reporter_location_2","Reporter County"],
	"reporter_location_3":["reporter_location_3","Reporter Sub County"],
	"reporter_location_4":["reporter_location_4","Reporter Parish"],
	"reporter_location_5":["reporter_location_5","Reporter Village"],
	"reporter_location_6":["reporter_location_6","Reporter Constituency"],

	"clients^contact_age_group":["clients^contact_age_group","Client Age Group"],
	"clients^contact_sex":["clients^contact_sex","Client Sex"],
	"clients^contact_national_id_type":["clients^contact_national_id_type","Client ID Type"],
	"clients^contact_nationality":["clients^contact_nationality","Client Nationality"],
	"clients^contact_lang":["clients^contact_lang","Client Language"],
	"clients^contact_tribe":["clients^contact_tribe","Client Tribe"],
	"clients^contact_location_0":["clients^contact_location_0","Client Region"], 
	"clients^contact_location_1":["clients^contact_location_1","Client District"],
	"clients^contact_location_2":["clients^contact_location_2","Client County"],
	"clients^contact_location_3":["clients^contact_location_3","Client Sub County"],
	"clients^contact_location_4":["clients^contact_location_4","Client Parish"],
	"clients^contact_location_5":["clients^contact_location_5","Client Village"],
	"clients^contact_location_6":["clients^contact_location_6","Client Constituency"],

	"clients^relationship":["clients^relationship","Reporter's Relationship to Client"],
	"clients^health":["clients^health","Client Health Status"],
	"clients^hiv":["clients^hiv","Client HIV Status"],
	"clients^marital":["clients^marital","Client Marital Status"],
	"clients^spouse_profession":["clients^spouse_profession","Client Spouse Profession"],
	"clients^household":["clients^household","Household Type"],
	"clients^household_head_occupation":["clients^household_head_occupation","Head of Household Occupation"],
	"clients^guardian_marital":["clients^guardian_marital","Parent/Guardian Marital Status"],
	"clients^school_level":["clients^school_level","School Level"],
	"clients^school_type":["clients^school_type","School Type"],
	"clients^disability":["clients^disability","Client Disablity"],

	"perpetrators^contact_age_group":["perpetrators^contact_age_group","Perp Age Group"],
	"perpetrators^contact_sex":["perpetrators^contact_sex","Perp Sex"],
	"perpetrators^contact_national_id_type":["perpetrators^contact_national_id_type","Perp ID Type"],
	"perpetrators^contact_nationality":["perpetrators^contact_nationality","Perp Nationality"],
	"perpetrators^contact_lang":["perpetrators^contact_lang","Perp Language"],
	"perpetrators^contact_tribe":["perpetrators^contact_tribe","Perp Tribe"],
	"perpetrators^contact_location_0":["perpetrators^contact_location_0","Perp Region"], 
	"perpetrators^contact_location_1":["perpetrators^contact_location_1","Perp District"],
	"perpetrators^contact_location_2":["perpetrators^contact_location_2","Perp County"],
	"perpetrators^contact_location_3":["perpetrators^contact_location_3","Perp Sub County"],
	"perpetrators^contact_location_4":["perpetrators^contact_location_4","Perp Parish"],
	"perpetrators^contact_location_5":["perpetrators^contact_location_5","Perp Village"],
	"perpetrators^contact_location_6":["perpetrators^contact_location_6","Perp Constituency"],
	"perpetrators^relationship":["perpetrators^relationship","Perpetrator's Relationship to Client"],
	"perpetrators^shareshome":["perpetrators^shareshome","Perpetrator's Shares Home with Client"],
	"perpetrators^health":["perpetrators^health","Perpetrator's Health Status"],
	"perpetrators^marital":["perpetrators^marital","Perpetrator's Marital Status"],
	"perpetrators^employment":["perpetrators^employment","Perpetrator's Profession"],
	"perpetrators^spouse_profession":["perpetrators^spouse_profession","Perpetrator's Spouse Profession"],

	"services^category_name":["services^category_name","Service Offered"],

	"referals^category_name":["referals^category_name","Referal"],
};

rk["case_cases_k"] = [ "cat_0", "cat_1", "cat_2", "cat_3", "cat_4", "gbv_related", "src", "priority", "status", "created_by", "escalated_to", "escalated_by", "assessment", "justice"];
re["case_cases_k"] = re["case_k"];

rk["case_reporters_k"] = ["reporter_age_group", "reporter_sex", "reporter_national_id_type", "reporter_nationality", "reporter_lang", "reporter_tribe", "reporter_location_0", "reporter_location_1", "reporter_location_2", "reporter_location_3", "reporter_location_4", "reporter_location_5","reporter_location_6"];
re["case_reporters_k"] = re["case_k"];

rk["case_clients_k"] = ["clients^contact_age_group", "clients^contact_sex", "clients^contact_national_id_type", "clients^contact_nationality", "clients^contact_lang", "clients^contact_tribe", "clients^contact_location_0", "clients^contact_location_1", "clients^contact_location_2", "clients^contact_location_3", "clients^contact_location_4","clients^contact_location_5","clients^contact_location_6", "clients^relationship", "clients^health", "clients^hiv", "clients^marital", "clients^spouse_profession", "clients^household", "clients^household_head_occupation", "clients^guardian_marital",  "clients^school_level", "clients^school_type",
 "clients^disability"];
re["case_clients_k"] = re["case_k"];

rk["case_perps_k"] = ["perpetrators^contact_age_group", "perpetrators^contact_sex", "perpetrators^contact_national_id_type", "perpetrators^contact_nationality",  "perpetrators^contact_lang", "perpetrators^contact_tribe", "perpetrators^contact_location_0", "perpetrators^contact_location_1", "perpetrators^contact_location_2", "perpetrators^contact_location_3", "perpetrators^contact_location_4", "perpetrators^contact_location_5", "perpetrators^contact_location_6", "perpetrators^relationship", "perpetrators^shareshome", "perpetrators^health", "perpetrators^marital", "perpetrators^employment", "perpetrators^spouse_profession"];
re["case_perps_k"] = re["case_k"];

rk["case_services_k"] = ["services^category_name"];
re["case_services_k"] = re["case_k"];

rk["case_referals_k"] = ["referals^category_name"];
re["case_referals_k"] = re["case_k"];

// ---

te["case_rpt_metric_tab"] = { div:["c x","%4"], c:
[
	{ arg:["","","0"] },
	{ input:["g","","case_metric","%2","radio","%9"] },
	{ li:["opth x y tc cb","%3","%1"], ev:["_tab"] }
]};

te["case_k_tag"] = { "rpt_axis_tag":["::case_k:0:1","xaxis"] };

te["case_k_r"] = { "rpt_axis_r":["xaxis","case_k_tag","::case_k:0:1"] };

te["case_rpt_ymenu"] = { c:
[
	{ div:["xx t bb_","vb"], c:
	[
		{ div:["c x"], c:[ { input:["g","","case_rpt_vw_t","0","radio","1"] }, { ac:["ay tabu","","_tab","xx y cb","Case"] } ] },
		{ div:["c x"], c:[ { input:["g","","case_rpt_vw_t","1","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Reporter"] } ] },
		{ div:["c x"], c:[ { input:["g","","case_rpt_vw_t","2","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Client"] } ] },
		{ div:["c x"], c:[ { input:["g","","case_rpt_vw_t","3","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Perpetrator"] } ] },
		{ div:["c x"], c:[ { input:["g","","case_rpt_vw_t","4","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Sevices"] } ] },
		{ div:["c x"], c:[ { input:["g","","case_rpt_vw_t","5","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Referals"] } ] },
		{ div:["e"] }
	]},
	{ div:["xx yy"], c:
	[
		{ div:[], c:[ { input:["g","","case_rpt_vw_tv","0","radio","1"] }, { div:["tabv"], uchk:["case_k_r",null,"case_cases_k"] } ] },
		{ div:[], c:[ { input:["g","","case_rpt_vw_tv","1","radio"] }, { div:["tabv"], uchk:["case_k_r",null,"case_reporters_k"] } ] },
		{ div:[], c:[ { input:["g","","case_rpt_vw_tv","2","radio"] }, { div:["tabv"], uchk:["case_k_r",null,"case_clients_k"] } ] },
		{ div:[], c:[ { input:["g","","case_rpt_vw_tv","3","radio"] }, { div:["tabv"], uchk:["case_k_r",null,"case_perps_k"] } ] },
		{ div:[], c:[ { input:["g","","case_rpt_vw_tv","4","radio"] }, { div:["tabv"], uchk:["case_k_r",null,"case_services_k"] } ] },
		{ div:[], c:[ { input:["g","","case_rpt_vw_tv","5","radio"] }, { div:["tabv"], uchk:["case_k_r",null,"case_referals_k"] } ] }
	]}
]};

te["case_rpt_options"] = {  c:
[
	
	{ input:["g","","type","bar","radio","1"] },
	{ ac:["r ay","","_rpt_opt","xx y02 cb",""], c:
	[
		{ div:["c w01_ t"], s:["opt",""] },
		{ s:["c x y ","Bar Chart"] },
		{ div:["e"] }			
	]},
	{ input:["g","","type","line","radio"] },
	{ ac:["r ay","","_rpt_opt","xx y02 cb",""], c:
	[
		{ div:["c w01_ t"], s:["opt",""] },
		{ s:["c x y ","Line Chart"] },
		{ div:["e"] }			
	]},

	{ input:["g","","stacked","stacked","checkbox","1"] },
	{ ac:["r ay","","_rpt_chk","xx y02 cb",""], c:
	[
		{ div:["c w01_ t"], s:["chk",""] },
		{ s:["c x y ","Stacked"] },
		{ div:["e"] }			
	]},

	{ input:["g","","sortrpt","1","checkbox"] },
	{ ac:["r ay","","_rpt_chk","xx y02 cb",""], c:
	[
		{ div:["c w01_ t"], s:["chk",""] },
		{ s:["c x y ","Sort by Total"] },
		{ div:["e"] }			
	]},
]};

te["case_rpt_"] = { c: // todo: load rpt_hdr params from db // 
[
	{ form:["tt","vrpt"], c:
	[
		{ div:["c"], c:
		[
			{ div:["ay","va"], ac:["","","_dd","x y04 cb",""], c:
			[
				{ s:["c x b h3",null] },
				//{ div:["c"], s:["h02 w02 awb",""] },
				{ div:["e"] }
			]},
			{ div:["dd w20 y ba gw sh","vdd"], ev:["_undd"], c:
			[
				// metrics
			]}	
		]},
		{ div:["d"], c:
		[
			{ div:["ay l20","va"], ac:["","","_dd","x y04 h02 cb ba",""], c:
			[
				{ s:["c x","Options"] },
				{ s:["c x t02 micon","more_vert"] },
				{ div:["e"] }
			]},
			{ div:["dd w18 mln7 mt y ba gw sh","vdd"], ev:["_undd"], case_rpt_options:[] }
		]},
		{ div:["d"], s:["",""], c:
		[
			{ div:["d"], c: // xaxis
			[
				{ div:["ba","va"], s:["",""], c:
				[	
					{ div:["d w03"], ac:["ay","","_dd","x y04",""],  c:[ { div:["h02 w02 awb"] } ] },
					{ div:["e"] }
				]},
				{ div:["dd x y mln50 w52 gw ba mt1","vdd_rpt"], ev:["_undd"], c:[ { case_rpt_ymenu:[null,null,null,null,null,null] } ] }
			]},
			{ div:["d"], uchk:["case_k_tag",null] },
			{ s:["d l20 r05 y07 cd","Y Axis:"] },
			{ div:[] },
		]},
		{ div:["d"], s:["",""], c:
		[
			{ uchk:["rpt_dist_r",null,"dist"]}, // xaxis (distribution options)
			{ s:["d l20 r05 y07 cd","X Axis:"] },
			{ div:["e"] },
		]},
		{ div:["e"], c:
		[ 
			{ arg:["","metrics",null] },
			{ input:["g","","rpt",null,"checkbox","1"] },
		]}
	]},
	{ div:["","case_rpt_vw-cases"], urpt:[] } 
]};

te["case_rpt"] = { case_rpt_:["::case_metrics:4:1","%2","%2","%3","%4","%7"] };  
te["case_rpt_percent"] = { case_rpt_:["Percent", "status","status","status","status","status","status","status", "-", "case_percent","case_percent"] };
te["case_rpt_count"] = { case_rpt_:["Count", "status","status","status","status","status","status","status", "-", "case_count","case_count"] };

te["case_rpt_main"] = { c:
[
	{ div:["g xx t15 bb_ s","vb"], c:
	[
		{ s:["c x y cd","Metric:"] },
		{ uchk:["case_rpt_metric_tab","count","case_metrics"] },
		// + add // todo add mutiple metrics to same canvas // then multi-metric with from different resources
		{ div:["d g"], c:
		[
			{ div:["w12 ay","va"], ac:["","","_dd","x cd",""], c:
			[
				{ div:["d w02 t04"], s:["h02 w02 awb",""] },
				{ s:["d x y","Saved Reports"] }, 
				{ div:["e"] }
			]},			
			{ div:["dd mln13 w25 ba sh gw cb","vdd"], ev:["_undd"], c:
			[
				{s:["xx y cd","- Saved Reports List -"] }
			]}
		]},
		{ div:["e"] }
	]},
	{ div:["","vrpt"], c:
	[
		{ div:[], c:[ { input:["g","","case_rptv","0","radio","1"] }, { p:["tabv","vt"], case_rpt_count:[] } ]},
		{ div:[], c:[ { input:["g","","case_rptv","0","radio"] }, { p:["tabv oh","vt"] } ] },
		{ div:[], c:[ { input:["g","","case_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","case_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","case_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","case_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","case_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","case_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
	]}
]};

// =========================================================================================

te["case_yesno_r"] = { c:
[
	{ input:["g","",null,"%0","radio","%9"] },
	{ ac:["c ay r05 r rg","","_opt","x cb bd_",""], c:
	[
		{ div:["c w01_ t"], s:["opt",""] },
		{ s:["c x y w07",null] },
		{ div:["e"] }			
	]}
]};

// ---

te["case_enum_lc"] = { c:
[
	{ div:[], c:
	[
		{ div:["c"], s:[null,null] },
		{ s:["c t h2 cr b",null] },
		{ div:["e"] }
	]},
	{ div:["",null], c:
	[
		{ li:["gww_ b02","va"], c:[ { div:["",null], ev:["_dd"], c: // ls
		[
			{ div:["",null], c:[ { p:[null,"a"], uchk:["taga",null,"","",null,null,null,null,null] } ] },
			{ div:["d w02 x y"],  c:[ { div:["h02 w02 awb"] } ] },
			{ div:["e"], c:[ { arg:["_c","","10"] }, { arg:["root_id_","",null] }, { u:[null] } ] }
		]} ]},			
		{ div:[null,"vdd"], ev:["_undd"] },
		{ u:[null] }
	]}
]};

te["case_enum_lsh"] = { c: 
[
	{ div:[], c:
	[
		{ div:["c"], s:[null,null] },
		{ s:["c t h2 cr b",null] },
		{ div:["e"] }
	]},
	{ div:["",null], c:
	[
		{ li:["gww_ b02","va"], c:
		[ 
			{ div:["",null], ev:["_dd"], c: // lsh
			[
				{ p:[null,"o"], c:
                        	[ 
                        		{ u:[null,null] }, 
                        		{ uchk:["tag",null,"","^", null,null,null,null,null] } 
                        	]},
				{ div:["d w02 x y"],  c:[ { div:["h02 w02 awb"] } ] }, 
				{ div:["e"], c:[ { arg:["_c","","10"] }, { arg:["root_id_","",null] }, { arg:["level","",null] }, { arg:["sort","",null] }, { u:[null] } ] }
			]},
			{ div:["g",null], arg:[".id","",null] } 
		]},			
		{ form:[null,"vdd"], ev:["_undd"] },
		{ u:[null] }
	]}
]};

te["case_enum_ls"] = { c:  
[
	{ div:[], c:
	[
		{ div:["c"], s:[null,null] },
		{ s:["c t h2 cr b",null] },
		{ div:["e"] }
	]},
        { div:["",null], c:
        [
                { li:["gww_ b02","va"], c:[ { div:["",null], ev:["_dd"], c: // ls
                [
                        { p:[null,"o"], c:
                        [ 
                        	{ u:[null,null] }, 
                        	{ uchk:["tag",null,"","^", null,null,null,null,null] } 
                        ]},
                        { div:["d w02 x y"],  c:[ { div:["h02 w02 awb"] } ] },
                        { div:["e"], c:[ { arg:["_c","","10"] }, { arg:["root_id_","",null] }, { arg:["sort","",null] }, { u:[null] } ] }
                ]} ]},
                { div:[null,"vdd"], ev:["_undd"] },
                { u:[null] } 
        ]}
]};

te["case_enum_sel"] = { c:
[
	{ div:[], c:
	[
		{ div:["c"], s:[null,null] },
		{ s:["c t h2 cr b",null] },
		{ div:["e"] }
	]},
	{ div:["",null], c:
	[
		{ li:["gww_ b02","va"], c:[ { div:[], ev:["_dd"], c: // ls
		[
			{ p:[null,"o"], uchk:["tag",null,"","^", "",null,null,null,null] },
			{ div:["d w02 x y"],  c:[ { div:["h02 w02 awb"] } ] },
			{ div:["e"] }
		]} ]},			
		{ div:[null,"vdd"], ev:["_undd"], c: // 
		[
			{ uchk:[null,"",null] }
		]}
	]}
]};

te["case_enum_tag_txa__"] = { p:["","txa"], c: // [nb] id(txa) used by uhilite
[ 
	{ input:[null,null,"","","text","",null], ev:["","_ky","","_uky"] }, 
	{ arg:["",null,null] }, // placeholder for upd
]};

te["case_enum_tag_txa_"] = { p:["","txa"], c: // [nb] id(txa) used by uhilite
[ 
	{ input:[null,null,"","","text","",null], ev:["","_ky","","_uky"] }, 
	{ arg:["",null,""] }, // placeholder for upd
]};

te["case_txt_"] = { c:
[
	{ s:["x y",null] },
	{ p:["","o"], c:[ { input:[null,"",null,null,"text","",null] } ] },
]};

// -----------------------

te["case_household_tag_txa"] = { case_enum_tag_txa_:["w21 xx tt b05","fullname__","","household_id"] };

te["case_household_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_household_tag_txa-%1-household_id-%0-", "category_ls-subcategories", "c w17", "case_household_tag_txa","r_", null,"case_household_tag_txa",null,"household_id",null,"", HOUSEHOLD_TYPE_ROOT_ID, "fullname", "noop","dd w21 gw_ ba_b", "noop"] };

// ---

te["case_guardian_marital_tag_txa"] = { case_enum_tag_txa_:["w21 xx tt b05","fullname__","","guardian_marital_id"] };

te["case_guardian_marital_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_guardian_marital_tag_txa-%1-guardian_marital_id-%0-", "category_ls-subcategories", "c w17", "case_guardian_marital_tag_txa","r_", null,"guardian_marital_id",null,"guardian_marital_id",null,"", MARITAL_STATUS_ROOT_ID, "fullname", "noop","dd w21 gw_ ba_b", "noop"] };

// ---

te["case_household_head_employment_tag_txa"] = { case_enum_tag_txa_:["w21 xx tt b05","fullname__","Select Employment Status","household_head_occupation_id"] };

te["case_household_head_employment_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_household_head_employment_tag_txa-%1-household_head_occupation_id-%0-", "category_ls-subcategories", "c w17", "case_household_head_employment_tag_txa","r_", null,"case_household_head_employment_tag_txa",null,"household_head_occupation_id",null,"", EMPLOYMENT_STATUS_ROOT_ID, "fullname", "noop","dd w20 gw_ ba_b", "noop"] };

// ---

te["case_spouse_employment_tag_txa"] = { case_enum_tag_txa_:["w21 xx tt b05","fullname__","Select Employment Status","spouse_profession_id"] };

te["case_spouse_employment_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_spouse_employment_tag_txa-%1-spouse_profession_id-%0-", "category_ls-subcategories", "c w17", "case_spouse_employment_tag_txa","r_", null,"case_spouse_employment_tag_txa",null,"spouse_profession_id",null,"", EMPLOYMENT_STATUS_ROOT_ID, "fullname", "noop","dd w21 gw_ ba_b", "noop"] };

// ---

te["case_hiv_tag_txa"] = { case_enum_tag_txa_:["w20 xx tt b05","fullname__","","hiv_id"] };

te["case_hiv_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_hiv_tag_txa-%1-hiv_id-%0-", "category_ls-subcategories", "c w17", "case_hiv_tag_txa","r_", null,"case_hiv_tag_txa",null,"hiv_id",null,"", HIV_STATUS_ROOT_ID, "fullname", "noop","dd w20 gw_ ba_b", "noop"] };

// ---

te["case_disability_tag_txa"] = { case_enum_tag_txa_:["w20 xx tt b05","fullname__","","disability_id"] };

te["case_disability_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_disability_tag_txa-%1-disability_id-%0-", "category_ls-subcategories", "c w17", "case_disability_tag_txa","r_", null, "case_disability_tag_txa",null,"disability_id",null,"", DISABILITY_ROOT_ID, "fullname", "noop","dd w20 gw_ ba_b", "noop"] };

// ---

te["case_school_level_tag_txa"] = { case_enum_tag_txa_:["w20 xx tt b05","fullname__","","school_level_id"] };

te["case_school_level_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_school_level_tag_txa-%1-school_level_id-%0-", "category_ls-subcategories", "c w17", "case_school_level_tag_txa","r_",null, "case_school_level_tag_txa",null,"school_level_id",null,"", SCHOOL_LEVEL_ROOT_ID, "fullname", "noop","dd w20 gw ba_b", "noop"] };

// --- 

te["case_school_type_tag_txa"] = { case_enum_tag_txa_:["w20 xx tt b05","fullname__","","school_type_id"] };

te["case_school_type_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_school_type_tag_txa-%1-school_type_id-%0-", "category_ls-subcategories", "c w17", "case_school_type_tag_txa","r_", null, "case_school_type_tag_txa",null,"school_type_id",null,"", SCHOOL_TYPE_ROOT_ID, "fullname", "noop","dd w20 gw_ ba_b", "noop"] };

// ---

te["case_employment_tag_txa"] = { case_enum_tag_txa_:["w21 xx tt b05","fullname__","Select Work Status","employment_id"] };

te["case_employment_enum"] = { case_enum_ls:["x y",null,"",  "tag-r_--o-case_employment_tag_txa-%1-employment_id-%0-", "category_ls-subcategories", "c w17", "case_employment_tag_txa","r_", null, "case_employment_tag_txa",null,"employment_id",null,"", EMPLOYMENT_STATUS_ROOT_ID, "fullname", "noop","dd w21 gw_ ba_b", "noop"] };

// --- 

te["case_health_tag_txa"] = { case_enum_tag_txa_:["w21 xx tt b05","fullname__","Select Health Status","health_id"] };

te["case_health_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_health_tag_txa-%1-health_id-%0-", "category_ls-subcategories", "c w17", "case_health_tag_txa","r_", null, "case_health_tag_txa",null,"health_id",null,"", HEALTH_STATUS_ROOT_ID, "fullname", "noop", "dd w21 gw_ ba_b", "noop"] };

// ---

te["case_shareshome_tag_txa"] = { case_enum_tag_txa_:["w20 xx tt b05","fullname__","","shareshome_id"] };

te["case_shareshome_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_shareshome_tag_txa-%1-shareshome_id-%0-", "category_ls-subcategories","c w17", "case_shareshome_tag_txa","r_", 
null, "case_shareshome_tag_txa",null,"shareshome_id",null,"", SHARES_HOME_ROOT_ID, "fullname", "noop","dd w20 gw_ ba_b", "noop"] };

// ---

te["case_rela_tag_txa"] = { case_enum_tag_txa_:["w20 xx tt b05","fullname__","Select Relationship","relationship_id"] };

te["case_rela_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_rela_tag_txa-%1-relationship_id-%0-", "category_ls-subcategories", "c w17", "case_rela_tag_txa","r_", null, "case_rela_tag_txa",null, "relationship_id",null,"",  RELATIONSHIP_ROOT_ID, "fullname", "noop", "dd w20 gw_ ba_b", "noop"] };

// ---

te["case_not_in_school_tag_txa"] = { case_enum_tag_txa_:["w62 xx tt b05","fullname__","Select Reason","not_in_school_id"] };

te["case_not_in_school_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_not_in_school_tag_txa-%1-not_in_school_id-%0-", "category_ls-subcategories", "c w59", "case_not_in_school_tag_txa","r_", null, "case_not_in_school_tag_txa",null,"not_in_school_id",null,"",  NOT_IN_SCHOOL_ROOT_ID, "fullname", "noop", "dd w62 gw_ ba_b", "noop"] };

// ---

te["case_loc_tag_txa"] = { case_enum_tag_txa_:["w38 xx tt b05","fullname__","Select Location","location_id"] };

te["case_loc_enum"] = { case_enum_lsh:["x y",null,"",
"tag-r_--o-case_loc_tag_txa-%1-location_id-%0-",   "category_ls-subcategories-h", "c w37", 
"case_loc_tag_txa","r_", 
null, "case_loc_tag_txa",null,"location_id",null,"",   
LOCATION_ROOT_ID, "", "fullname", "noop",
"category_lsh_main-categories", LOCATION_ROOT_ID,
"dd w65 gw_ ba_b mtn1", 
"noop"] };

// ---

te["case_lang_tag_txa"] = { case_enum_tag_txa_:["w21 xx tt b05","fullname__","Select Language","lang_id"] };

te["case_lang_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_lang_tag_txa-%1-lang_id-%0-", "category_ls-subcategories", "c w17", "case_lang_tag_txa","r_", null, "case_lang_tag_txa", null, "lang_id", null,"", LANGUAGE_ROOT_ID, "fullname", "noop", "dd w21 gw_ ba_b", "noop"] };

// ---

te["case_tribe_tag_txa"] = { case_enum_tag_txa_:["w21 xx tt b05","fullname__","Select Tribe","tribe_id"] };

te["case_tribe_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_tribe_tag_txa-%1-tribe_id-%0-", "category_ls-subcategories", "c w16", "case_tribe_tag_txa","r_", null, "case_tribe_tag_txa",null, "tribe_id",null,"",  TRIBE_ROOT_ID, "fullname", "noop", "dd w20 gw_ ba_b", "noop"] };

// ---

te["case_nationality_tag_txa"] = { case_enum_tag_txa_:["w21 xx tt b05","fullname__","Select Nationality","nationality_id"] };

te["case_nationality_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_nationality_tag_txa-%1-nationality_id-%0-", "category_ls-subcategories", "c w17", "case_nationality_tag_txa","r_", null, "case_nationality_tag_txa",null,"nationality_id",null,"", NATIONALITY_ROOT_ID, "fullname", "noop", "dd w21 gw_ ba_b", "noop"] };

// ---

te["case_national_id_type_tag_txa"] = { case_enum_tag_txa_:["w21 xx tt b05","fullname__","Select ID Type","national_id_type_id"] };

te["case_national_id_type_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_national_id_type_tag_txa-%1-national_id_type_id-%0-", "category_ls-subcategories", "c w16", "case_national_id_type_tag_txa","r_", null, "case_national_id_type_tag_txa",null,"national_id_type_id",null,"",  NATIONAL_ID_TYPE_ROOT_ID, "fullname", "noop", "dd w20 gw_ ba_b", "noop"] };

// ---

te["case_sex_tag_txa"] = { case_enum_tag_txa_:["w21 xx tt b05","fullname__","Select Gender","sex_id"] };

te["case_sex_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_sex_tag_txa-%1-sex_id-%0-", "category_ls-subcategories", "c w17", "case_sex_tag_txa","r_", null, "case_sex_tag_txa",null,"sex_id",null,"",  SEX_ROOT_ID, "fullname", "noop", "dd w21 gw_ ba_b", "noop"] };

// ---

te["case_age_tag_txa"] = { case_enum_tag_txa_:["w21 xx t08 b05","fullname__","Select Age Group","age_group_id"] };

te["case_age_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_age_tag_txa-%1-age_group_id-%0-", "category_ls-subcategories", "c w17", "case_age_tag_txa","r_", null, "case_age_tag_txa",null, "age_group_id",null,"",  AGE_GROUP_ROOT_ID, "fullname", "noop", "dd w21 gw_ ba_b", "noop"] };

// ----

te["case_referal_sel_sub"] = { div:["","sub"], c:
[
	{ arg:["case_ed_sub_other_referal-r_-_case_referals_-_case_other_referal_","",CASE_REFERAL_OTHER_ID] },
]};

te["case_referal_enum"] = { case_enum_lc:["x y",null,"",  "taga-r_--a--%1-category_id-%0-%2", "case_lc_main-subcategories", "referals", "c w40",    
null,"referal_del-referals-case_id"," %1","category_id"," %0","%2",  
CASE_REFERALS_ROOT_ID,"noop", 
"dd w50 ba_b gw_","case_referal_sel_sub"] };

// ---

te["case_service_sel_sub"] = { div:["","sub"], c:
[
	{ arg:["case_ed_sub_referals-r_-ve-_case_referals_","",CASE_SERVICE_REFERAL_ID] },
	{ arg:["case_ed_sub_police_ref-r_-ve-_case_police_ref_","",CASE_SERVICE_POLICE_ID] },
	{ arg:["case_ed_sub_other_service-r_-ve-_case_other_service_","",CASE_SERVICE_OTHER_ID] },
]};

te["case_service_enum"] = { case_enum_lc:["x y",null,"","taga-r_--a--%1-category_id-%0-%2", "case_lc_main-subcategories", "services", "c w41",    
null, "service_del-services-case_id"," %1","category_id"," %0"," %2",  
CASE_SERVICES_ROOT_ID,"noop", 
"dd w50 ba_b gw_","case_service_sel_sub"] };

// ---

te["case_knowabout116_tag_txa"] = { case_enum_tag_txa_:["w49 xx tt b05","fullname__","","knowabout116_id"] };

te["case_knowabout116_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_knowabout116_tag_txa-%1-knowabout116_id-%0-", "category_ls-subcategories", "c w41", "case_knowabout116_tag_txa","r_", null,"case_knowabout116_tag_txa",null,"knowabout116_id",null,"", CASE_KNOW_ABOUT_116_ROOT_ID, "fullname", "noop", "dd w45 gw_ ba_b", "noop"] };

// ---

te["case_justice_tag_txa"] = { case_enum_tag_txa_:["w30 xx tt b05","fullname__","","justice_id"] };

te["case_justice_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_justice_tag_txa-%1-justice_id-%0-", "category_ls-subcategories", "c w25", "case_justice_tag_txa","r_", null,"case_justice_tag_txa",null,"justice_id",null,"", CASE_JUSTICE_ROOT_ID, "fullname", "noop", "dd w30 gw_ ba_b", "noop"] };

// ---

te["case_assessment_tag_txa"] = { case_enum_tag_txa_:["w30 xx tt b05","fullname__","","assessment_id"] };

te["case_assessment_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_assessment_tag_txa-%1-assessment_id-%0-", "category_ls-subcategories", "c w25", "case_assessment_tag_txa","r_", null,"case_assessment_tag_txa",null,"assessment_id",null,"", CASE_ASSESSMENT_ROOT_ID, "fullname", "noop", "dd w30 gw_ ba_b", "noop"] };

// ---

te["case_escalated_matrix_r"] = { arg:["role","","::user_role:6:3"] };

te["case_escalated_to_args"] = { u:["case_escalated_matrix_r","auth"] };

te["case_escalated_to_tag_txa"] = { case_enum_tag_txa__:["w37 xx tt b05","usn__","","escalated_to_id","0"] };

te["case_escalated_to_enum"] = { case_enum_ls:["x y",null,"", 
"tag-r_--o-case_escalated_to_tag_txa-%1-escalated_to_id-%0-", "user_ls-users", "c w18", 
"case_escalated_to_tag_txa","r_", 
null,"case_escalated_to_tag_txa",null,"escalated_to_id",null,"",  
"", "usn", "case_escalated_to_args", 
"dd w29 gw_ ba_b", 
"noop"] };

// ---

te["case_priority_r"] = { div:[], ac:["ay","","_sel","xx tt b05 cb",""], c:
[
	{ s:["","%1"] },
	{ div:["e"], c:[ { arg:["id-0","","%0"] } ] }
]};

te["case_priority_enum"] = { case_enum_sel:["x y",null,null, "tag-r_--o--::case_priority:0:1-priority-%0-", "c w13",  null," ::case_priority:0:1","priority"," %0","", 
"dd w17 ba_b gw_ cb","case_priority_r","case_priority_form"] };

// ---

te["case_status_r"] = { div:[], ac:["ay","","_sel","xx tt b05 cb",""], c: // 
[
	{ s:["","%1"] },
	{ div:["e"], c:[ { arg:["id-0","","%0"] } ] }
]};

te["case_status_enum"] = { case_enum_sel:["x y",null,null, "tag-r_--o--::case_status:0:1-status-%0-", "c w13",  null," ::case_status:0:1","status"," %0","", 
"dd w17 ba_b gw_ cb","case_status_r","case_status_form"] };

// ---

te["case_category_sel_sub"] = { div:["","sub"], c:
[
	{ arg:["case_ed_sub_medical_exam,case_ed_sub_medical_exam-r_-ve-_case_medical_exam_","",CASE_CATEGORY_PHYSICAL_N_SEXUAL_ABUSE_ID] },
	{ arg:["case_ed_sub_incidence-r_-ve-_case_incidence_","",CASE_CATEGORY_SEXUAL_ABUSE_ID] },
	{ arg:["case_ed_sub_justice-r_-ve-_case_justice_","",CASE_CATEGORY_ABUSE_ID] },
]};

te["case_category_tag_txa"] = { case_enum_tag_txa_:["w57 xx tt b05","fullname__","Select Category","case_category_id"] };

te["case_category_enum"] = { case_enum_lsh:["x y","Case Category","*",
"tag-r_--o-case_category_tag_txa-%1-case_category_id-%0-%2", "category_ls-subcategories-h", "c w56",  // todo: category_lsh
"case_category_tag_txa","r_", 
":v:cases:case_category_id", "case_category_tag_txa",":v:cases:case_category","case_category_id",":v:cases:case_category_id",":v:cases:case_category_fullname_id",   
CASE_CATEGORY_ROOT_ID, "", "fullname", "noop",
"category_lsh_main-categories",CASE_CATEGORY_ROOT_ID,
"dd w60_ gw_ ba_b mtn1",
"case_category_sel_sub"] };

// --------------------------

te["case_ed_sub_other_referal"] = { div:["t15"], c: // 362009:other referal
[
	{ arg:["","",""] },
	{ div:["w01 tt bb2_b abs"] },
	{ div:["ll"], case_txt_:["Specify Other Referal","gws_ w45 x tt b05","specify_referal",":v:cases:specify_referal",""] }
]};

te["case_ed_sub_other_service"] = { div:["t15"], c: // 362042:others service
[
	{ arg:["","",""] },
	{ div:["w01 tt bb2_b abs"] },
	{ div:["ll"], case_txt_:["Specify Other Service","gws_ w45 x tt b05","specify_service",":v:cases:specify_service",""] }
]};

te["case_ed_sub_police_ref"] = { div:["t15"], c: // 362036:report_to_police
[
	{ arg:["","",""] },
	{ div:["w01 tt bb2_b abs"] },
	{ div:["ll"], case_txt_:["Enter REF/CRB Number","gws_ w45 x tt b05","police_ob_no",":v:cases:police_ob_no","Enter REF/CRB Number"] }
]};

te["case_ed_sub_referals"] = { div:["t15"], c: // 117:referal
[
	{ arg:["","",""] },
	{ div:["w01 tt bb2_b abs"] },
	{ div:["ll _ba_"], case_referal_enum:["Referals",":v:cases:referals"] },
	{ p:["","_case_other_referal_"], usub:["case_ed_sub_other_referal","r_",":v:cases:referals",CASE_REFERAL_OTHER_ID] },
]};

te["case_ed_sub_incidence_counseling_loc"] = { case_txt_:["Which organisation was s/he referred to?","gws_ w30 x tt b05","counseling_org",":v:cases:counseling_org",""] };

te["case_ed_sub_incience_hiv_result_art"] = { c:
[
	{ s:["x y ","Has the client been initiated on ART?"] },
	{ p:["","o"], c:
	[
		{ uchk:["case_yesno_r",":v:cases:is_art_given","yesno","",  "is_art_given"," %2"] },
		{ div:["e"] }		
	]}
]};

te["case_ed_sub_incience_hiv_result_pep"] = { c:
[
	{ s:["x y ","Was PEP Administered?"] },
	{ p:["","o"], c:
	[
		{ uchk:["case_yesno_r",":v:cases:is_pep_given","yesno","", "is_pep_given"," %2"] },
		{ div:["e"] }		
	]}
]};

te["case_ed_sub_incidence_hiv_result"] = { c:
[
	{ s:["x y ","What is the Result of the HIV test?"] },
	{ p:["","o"], c:
	[
		{ uchk:["case_yesno_r",":v:cases:hiv_test_result","yesno","", "hiv_test_result"," %3"] },
		{ div:["e","sub"], arg:["case_ed_sub_incience_hiv_result_pep,case_ed_sub_incience_hiv_result_art-r_-hivre-hivra-0","","0,1"] }	
	]},
	{ p:["abs t15","hivra"], usub:["case_ed_sub_incience_hiv_result_pep,case_ed_sub_incience_hiv_result_art","r_",":v:cases:hiv_test_result","0,1"] }
]};

te["case_ed_sub_incidence_where"] = { c:
[
	{ case_txt_:["Where was the Incidence Reported?","gws_ w35 x tt b05","incidence_location",":v:cases:incidence_location","Enter Incidence Location"] },
	{ case_txt_:["Incidence Police Ref. No.","gws_ w35 x tt b05","incidence_ref_no",":v:cases:incidence_ref_no","Enter Police Ref No."] }
]};

te["case_ed_sub_incidence"] = { div:["xx ba mt15"], c:
[
	{ arg:["","","case_ed_sub_medical_exam"] },
	{ div:["t15"], c:
	[
		{ div:["c w35"], c:
		[
			{ s:["x y","When did the incident take place?"] },
			{ li:["w20 gws_ bd","va"], c:[ { div:[""], ev:["_dd"], c: // kf_d:["Date"," :d:dmy:0: ","chan_ts",":k:calls_f:chan_ts","chan_ts",":k:calls_f:chan_ts"] },
			[					
				{ p:["c w16 x t03","o"], c:[ { p:["","calv"], ucalv:[" :d:dmy:0: ","incidence_when",":v:cases:incidence_when"] } ] }, 
				{ div:["d w02 x y content-hidden_"],  c:[ { div:["h02 w02 awb"] } ] },
				{ div:["d w02 x y content-shown_"],  c:[ { div:["h02 w02 awt"] } ] },
				{ div:["e"] }
			]} ]},
			{ div:["dd w21 sh xx b10 ba mtn1 gw","vdd"], ev:["_undd"], c:
			[ 
				{ div:[], c:
				[
					{ ucal:["incidence_when",":v:cases:incidence_when","noop","1","", ""] },
					{ div:["e"] },
				]}
			]}
        	]},
        	{ div:["e"] }
	]},
	
	{ div:["t15","inci"], c:
	[
        	{ div:["c w35"], c:
		[
			{ s:["l y","Was the Incident Reported?"] },
			{ p:["","o"], c:
			[
				{ uchk:["case_yesno_r",":v:cases:is_incidence_reported","yesno","",  "is_incidence_reported"," %2"] }, // %4
				{ div:["e","sub"], arg:["case_ed_sub_incidence_where-r_-inci-incw-0","","1"] }
			]}
		]},
		{ p:["d w35 ll","incw"], usub:["case_ed_sub_incidence_where","r_",":v:cases:is_incidence_reported","1"] },
		{ div:["e"] }
	]},
	
	{ div:["t15","hivt"], c:
	[
		{ div:["c w35"], c:
		[
			{ s:["x y ","Has the Client been tested for HIV?"] },
			{ p:["","o"], c:
			[
				{ uchk:["case_yesno_r",":v:cases:is_hiv_tested","yesno","",  "is_hiv_tested"," %2"] }, // " %4"
				{ div:["e","sub"], arg:["case_ed_sub_incidence_hiv_result-r_-hivt-hivre-0","","1"] }
			]}
		]},
		{ p:["d w35 ll","hivre"], usub:["case_ed_sub_incidence_hiv_result","r_",":v:cases:is_hiv_tested","1"] },
		{ div:["e"] }
	
	]},
	{ div:["t15"], c:
	[
		{ div:["c w35"], c:
		[
			{ s:["x y ","Was ECP provided to prevent Un-intended pregnancies? "] },
			{ p:["","o"], c:
			[
				{ uchk:["case_yesno_r",":v:cases:is_ecp_given","yesno","",  "is_ecp_given"," %2"] },
				{ div:["e"] }		
			]}
		]},
		{ div:["e"] }	
	]},
	
	{ div:["y15","cou"], c:
	[
		{ div:["c w35"], c:
		[
			{ s:["x y ","Did the client get counselling / referred for Counselling and further psycho-social support?"] },
			{ p:["","o"], c:
			[
				{ uchk:["case_yesno_r",":v:cases:is_counselling_given","yesno","",  "is_counselling_given"," %2"] },
				{ div:["e","sub"], arg:["case_ed_sub_incidence_counseling_loc-r_-cou-coloc-0","","1"] }
			]}
		]},
		{ p:["d w35 ll","coloc"], usub:["case_ed_sub_incidence_counseling_loc","r_",":v:cases:is_counselling_given","1"] },
		{ div:["e"] }	
	]}
	
]};

te["case_ed_sub_medical_exam"] = { div:["xx ba mt15"], c:
[
	{ arg:["","","case_ed_sub_medical_exam"] },
	{ div:["yy"], c:
	[
		{ div:[""], c:
		[
			{ s:["x y","Has the client received medical examination?"] },
			{ p:["","o"], c:
			[
				{ uchk:["case_yesno_r",":v:cases:is_medical_exam_done","yesno","",  "is_medical_exam_done"," %2"] },
				{ div:["e"] }		
			]}
		]},
		{ div:["e"] }
	]}
]};

te["case_ed_sub_justice"] = { div:["mt15"],  c:
[
	{ div:["c w29 r20 "], case_justice_enum:["State of the Case in the Justice System",":v:cases:justice_id",":v:cases:justice"," %0"] },
	{ div:["c w29"], case_assessment_enum:["General Case Assessment",":v:cases:assessment_id",":v:cases:assessment"," %0"] },
	{ div:["e"] }
]};

// ---

te["case_reporter_uuid_arg"] = { arg:["","reporter_uuid_id","%0"] };

te["case_uuid_arg"] = { arg:["","uuid",":v:cases_uuid:uuid"] };

te["case_form_col_1"] = { c:
[
	{ div:["t25"], c:
	[
		{ div:["w60 _ba_"], case_category_enum:[] },
		{ div:["t15"], c:
		[
			{ div:[], c:
			[
				{ s:["c x y","Is this Case GBV Related?"] },
				{ s:["c t cr b h2","*"] },
				{ div:["e"] }
			]},
			{ p:["","o"], c:
			[
				{ uchk:["case_yesno_r",":v:cases:gbv_related","yesnoo","",   "gbv_related"," %2"] },
				{ div:["e"] }		
			]}
		]},
		{ div:["e"] }
	]},

	{ p:["","_case_medical_exam_"], usub:["case_ed_sub_medical_exam,case_ed_sub_medical_exam","r_",":v:cases:case_category_fullname_id", CASE_CATEGORY_PHYSICAL_N_SEXUAL_ABUSE_ID] },	
	{ p:["","_case_incidence_"], usub:["case_ed_sub_incidence","r_",":v:cases:case_category_fullname_id",CASE_CATEGORY_SEXUAL_ABUSE_ID] },
	
	{ div:["t15"], c:
	[
		{ div:[], c:
		[
			{ s:["c x y","Case Narrative"] },
			{ s:["c t h2 cr b","*"] },
			{ div:["e"] }
		]},
		{ p:["","o"], c:[ { textarea:["w60 wx60 mh15 xx yy ba","","narrative",":v:cases:narrative","What Really Happened?"] } ] }
	]},
	
	{ div:["t15"], c:
	[
		{ div:[], c:
		[
			{ s:["c x y","Case Plan"] },
			{ s:["c t h2 cr b",""] },
			{ div:["e"] }
		]},
		{ p:["","o"], c:[ { textarea:["w60 wx60 mh15 xx yy ba","","plan",":v:cases:plan","Enter Case Plan"] } ] }
	]},
	
	{ p:["_ba_","_case_justice_"], usub:["case_ed_sub_justice","r_",":v:cases:case_category_fullname_id",CASE_CATEGORY_ABUSE_ID] },
	
	{ div:["t15 b30"], c:
	[
		{ div:["c w17 r20 _ba_"], case_priority_enum:["Priority","*",":v:cases:priority"] },
		{ div:["c w17 r20 _ba_"], case_status_enum:["Status","*",":v:cases:status"] },
		{ div:["c w22 _ba_"], case_escalated_to_enum:["Escalated To",":v:cases:escalated_to_id",":v:cases:escalated_to"," %0"] },
		{ div:["e"] }
	]}
]};

te["case_form_col_0"] = {  c:   
[
	{ div:["tt",""], c:
	[
		{ u:["case_form_reporter","reporters"] }, // reporter_id
	
		{ u:[null,"reporters_uuid"] }, // caller (reporter_uuid_id)
	]},
	
	{ p:["t15","clients_case"], c:
	[
		{ div:[], c:
		[
			{ s:["xx yy b n","Clients"] },
			{ div:["e"] }
		]},
		{ p:["","a"], u:["case_form_client_r","clients"] },
		{ div:[], c:
		[
			{ div:["c"], c:
			[
				{ ac:["ay x","case_client_new-r_-^","_vp","bd16 cb",""], c:
				[ 
					{ s:["c x y h01_ w01_ gws_ tc b h3 bd16 cb","+"] }, 
					{ s:["c x y","Add a Client"] }, 
					{ div:["e"], c:[ { arg:["case_id-6","","%0"] } ] } 
				]},
				{ div:["g"], c:[ { arg:["","","case_form_client_r-clients-clients-a"] } ] }
			]},
			{ div:["e"] }
		]}
	]},
	
	{ div:["t15","perpetrators_case"], c:
	[
		{ div:[], c:
		[
			{ s:["xx yy b n","Perpetrators"] },
			{ div:["e"] }
		]},
		{ p:["","a"], u:["case_form_perpetrator_r","perpetrators"] },
		{ div:[], c:
		[	
			{ div:["c"], c:
			[
				{ ac:["ay x","case_perpetrator_new-r_-^","_vp","bd16 cb",""], c:
				[ 
					{ s:["c x y h01_ w01_ gws_ tc b h3 bd16 cbb","+"] }, 
					{ s:["c l r10 y","Add a Perpetrator"] }, 
					{ div:["e"], c:[ { arg:["case_id-6","","%0"] } ] } 
				]},
				{ div:["g"], arg:["","","case_form_perpetrator_r-perpetrators-perpetrators-a"] }
			]},
			{ div:["e"] }
		]}
	]},
	
	{ div:["t15","attachments_case"], c:
	[
		{ div:[], c:
		[
			{ s:["xx yy b n","Related Files"] },
			{ div:["e"] }
		]},
		{ p:["","a"], u:["case_attachment","attachments"] },
		{ div:[], c:
		[
			{ div:["c"], c:
			[
				{ ac:["ay x","case_attachment_upload--attachments_case-a","_file_dialog","bd16 cb",""], c:
				[ 
					{ s:["c x y h01_ w01_ gws_ tc b h3 bd16 cb","+"] }, 
					{ s:["c xx y","Attach a File"] }, 
					{ div:["e"], c:[ { arg:["case_id-12","","%0"] } ] } 
				]}
			]},
			{ div:["e"] }
		]}
	]},
		
	{ div:["t15"], c:
	[ 
		{ div:["_ba_"], case_service_enum:["Services Offered",":v:cases:services"] },
		{ p:["bl2_b","_case_referals_"], usub:["case_ed_sub_referals","r_",":v:cases:services",CASE_SERVICE_REFERAL_ID] },
		{ p:["bl2_b","_case_police_ref_"], usub:["case_ed_sub_police_ref","r_",":v:cases:services",CASE_SERVICE_POLICE_ID] },
		{ p:["bl2_b","_case_other_service_"], usub:["case_ed_sub_other_service","r_",":v:cases:services",CASE_SERVICE_OTHER_ID] },
	]},
		
	{ div:["y15"], c:
	[
		{ div:["_ba_"], case_knowabout116_enum:["How did you know about 116?",":v:cases:knowabout116_id",":v:cases:knowabout116"," %0"] }
	]},
]};

te["case_form_"] = { div:["","ve"], s:["mw110",""], c: // new case // div:[" y15 gw"], 
[		
	{ div:["x20 tt","va"], c:
	[
		{ div:["c x t02"], ac:["","","_uvw","h2 x y bd16 gb cw micon","arrow_back"] }, // { u:[null] },	
		{ s:["c x08 tt h2 b",CASE_ID_PREFIX] },
		{ s:["c tt h2 b w40",null] },
		{ div:["e"] }
	]},
	
	{ div:["x20 t"], c:[ { p:["c w100","nb"], c:[ { u:["nb","cases_nb"] }, { u:["nb","newcase_nb"] } ] }, { div:["e"] } ] },
					
	{ div:["x20 w130_"], c:
	[
		{ div:["c w45_ r50"], case_form_col_0:[null] },
		{ div:["c w75_"], case_form_col_1:[] },
		{ div:["e"] }
	]},
		
	{ div:["x20 y30 w110"], c:
	[
		{ div:["d w12"], c:
		[
			{ ac:["btn ao",null,"_case_postj","y tc gb b cw",null] },
			{ div:["savl"], s:["yy tc bd go b n cw","Saving..."] }
		]},

		{ div:["d x35","va"], ac:["w12 ao",null,null,"y04 tc cd ba","Cancel"], c:  // todo: on cancel notify that changes will be lost	
		[ 
			{ arg:["",".id","%0"] },
			{ div:["e"], c:
			[ 
				{ arg:["",".id","-1"] }, 
				{ arg:["","case_id",":v:cases:id"] }, 
				{ u:["case_reporter_uuid_arg","reporters_uuid"] }
			]}
		]},
		
		{ p:["e","o"], c:
		[
			{ arg:["",".id","%0"] },
			{ div:[], c:
			[
				{ arg:["","disposition_id",null] },
				// todo: override if reporter_uuid exist
			]},
			{ u:["case_uuid_arg","cases_uuid"] }, // used when creating new case
		]},
	]}
]};

te["case_ed"] = { case_form_:[":v:cases:id", "case_form_reporter_followup", "case_ed-cases","Update", "case_vw_id-cases_uuid-vf","_u", DISPOSITION_ID_CASE_EDIT] };

te["case_new"] = { case_form_:["NEW CASE", "case_form_reporter_new_case", "case_new-cases","Create", "","_uvw", DISPOSITION_ID_NEW_CASE] };

te["case_update"] = { div:["w65 ma sh__ gw_"], c:
[
        { div:["t15 x15"], c:
        [
                { s:["c ll tt h3 b",CASE_ID_PREFIX] },
                { s:["c x tt h3 b","%0"] },
		{ ac:["d","","_uvp","x y03 h cb","&Cross;"] },
                { div:["e"] }
        ]},
        { div:["","ve"], s:["x20",""], c:
        [
                { div:["x y"], c:[ { p:["c w55","nb"], u:["nb","cases_nb"] }, { div:["e"] } ] },
                
                // todo: case_followup_vw_r ?

                { div:["t15"], c:
		[
			{ div:[], c:
			[
				{ s:["c x y","Case Plan Update"] },
				{ s:["c t h2 cr b","*"] },
				{ div:["e"] }
			]},
			{ p:["","o"], c:[ { textarea:["w60 wx60 mh15 xx yy gws","","plan","","Case Update"] } ] }
		]},
	
                { div:[], usub:["case_ed_sub_justice","r_",":v:cases:case_category_fullname_id","87"] },

                { div:["y15"], c:
		[
			{ div:["c w17 r20"], case_priority_enum:["Priority","*",":v:cases:priority"] },
			{ div:["c w17 r20"], case_status_enum:["Status","*",":v:cases:status"] },
			{ div:["c w22"], case_escalated_to_enum:["Escalated To",":v:cases:escalated_to_id",":v:cases:escalated_to"," %0"] },
			{ div:["e"] }
		]},

		{ div:["y15"], c:
                [
                        { div:["d xx"], c:
                        [
                                { ac:["btn w22 ao","case_update-cases","_case_postj_update","y gb cw tc","Update"] },
                                { div:["savl w20 ll t30 b05"], s:["y go cw tc bd","Updating ..."] },
                        ]},
                        { p:["e","o"], c:
                        [
                                { arg:["",".id","%0"] },
                                { div:[], c:
				[
					{ arg:["","disposition_id",DISPOSITION_ID_CASE_UPDATE] },
					// todo: override disposition if reporter_uuid exist
				]},
				{ u:["case_reporter_uuid_arg","reporters_uuid"] }
                        ] },
                        { div:["e"] }
                ]}
        ]}
]};

// ------------------------------------------------------------------------

te["case_vw_val_cat_tr"] = { c:
[
	{ s:["x tt tr v",null] },
	{ div:["x y n mh02 bd tr"], uval:[null,null] }
]};

te["case_vw_val_cat"] = { c:
[
	{ s:["x tt v",null] },
	{ div:["x y n mh02 bd"], uval:[null,null] }
]};

te["case_vw_val_tr"] = { c:
[
	{ s:["x tt v tr",null] },
	{ s:["x y n mh02 bd tr",null] }
]};

te["case_vw_val"] = { c:
[
	{ s:["x tt v",null] },
	{ s:["x y n mh02 bd",null] }
]};

te["case_notif_del"] = { div:["gp ml mt"], c:
[ 
        { s:["c x y cr","Deleted"] }, 
        { ac:["d","","_rm","x y","&Cross;"] },
        { div:["e"] }
]};

// ----

te["case_vw_sub_incidence_counseling_loc"] = { case_vw_val:["Which organisation was s/he referred to?",":v:cases:counseling_org"] };

te["case_vw_sub_incience_hiv_result_art"] = { case_vw_val:["Has the client been initiated on ART?",":v:cases:is_art_given::yesno:2"] };

te["case_vw_sub_incience_hiv_result_pep"] = { case_vw_val:["Was PEP Administered?",":v:cases:is_pep_given::yesno:2"] };

te["case_vw_sub_incidence_hiv_result"] = { c:
[
	{ case_vw_val:["What is the Result if HIV Test?",":v:cases:hiv_test_result::yesno:2"] },
	{ div:["abs t15"], usub:["case_vw_sub_incience_hiv_result_pep,case_vw_sub_incience_hiv_result_art","r_",":v:cases:hiv_test_result","0,1"] }
]};

te["case_vw_sub_incidence_where"] = { c:
[
	{ case_vw_val:["Where was the Incidence Reported?",":v:cases:incidence_location"] },
	{ case_vw_val:["Incidence Police Ref. No.",":v:cases:incidence_ref_no"] }
]};

te["case_vw_sub_incidence"] = { c:
[
	{ div:["t15"], c:
	[
		{ div:["c w30"], case_vw_val:["When did the incident take place?",":v:cases:incidence_when:d:dmy:"] }, //
        	{ div:["e"] }
	]},
	
	{ div:["t15"], c:
	[
        	{ div:["c w30"], case_vw_val:["Was the Incident Reported?",":v:cases:is_incidence_reported::yesno:2"] },
		{ div:["d w30 ll"], usub:["case_vw_sub_incidence_where","r_",":v:cases:is_incidence_reported","1"] },
		{ div:["e"] }
	]},
	
	{ div:["t15"], c:
	[
		{ div:["c w30"], case_vw_val:["Has the Client been tested for HIV?",":v:cases:is_hiv_tested::yesno:2"] },
		{ div:["d w30 ll"], usub:["case_vw_sub_incidence_hiv_result","r_",":v:cases:is_hiv_tested","1"] },
		{ div:["e"] }
	]},
	{ div:["t15"], c:
	[
		{ div:["c w30"], case_vw_val:["Was ECP provided to prevent Un-intended pregnancies?",":v:cases:is_ecp_given::yesno:2"] },
		{ div:["e"] }	
	]},
	
	{ div:["t15"], c:
	[
		{ div:["c w30"], case_vw_val:["Did the client get counselling / referred for Counselling and further psycho-social support?",":v:cases:is_counselling_given::yesno:2"] },
		{ p:["c w39 ll"], usub:["case_vw_sub_incidence_counseling_loc","r_",":v:cases:is_counselling_given","1"] },
		{ div:["e"] }	
	]}
]};

te["case_vw_sub_medical_exam"] = { c:
[
	{ div:["t15"], c:
	[
		{ div:["c w30"], case_vw_val:["Has the client received medical examination?",":v:cases:is_medical_exam_done::yesno:2"] },
		{ div:["e"] }
	]}
]};

te["case_vw_sub_other_referal"] = { div:["tt"], c: // 362009:other
[
	{ case_vw_val:["Specify Other Referal",":v:cases:specify_referal"] }
]};

te["case_vw_sub_other_service"] = { div:["l tt bl2_b"], c: // 362042:others
[
	{ case_vw_val:["Specify Other Service",":v:cases:specify_service"] }
]};

te["case_vw_sub_police_ref"] = { div:["tt"], c: // 362036:report_to_police
[
	{ case_vw_val:["Police REF/CRB Number",":v:cases:police_ob_no"] }
]};

te["case_vw_sub_referals"] = { div:[""], c: // 117:referal
[
	{ s:["x tt b","Referals"] },
	{ div:["r05 b05 n"], c:
	[ 
		{ uchk:["tagv",":v:cases:referals","","",  "x y bd gws"," %1"] }, 
		{ div:["e"] }
	]},
	{ div:[], usub:["case_vw_sub_other_referal","r_",":v:cases:referals",CASE_REFERAL_OTHER_ID] },
]};

te["case_vw_sub_justice"] = { div:["tt"], c:
[
	{ div:["c w30"], case_vw_val_cat:["State of the Case in the Justice System","",":v:cases:justice"] },
	{ div:["c w30"], case_vw_val_cat:["General Case Assessment","",":v:cases:assessment"] },
	{ div:["e"] }
]};

// ---

te["case_vw_col_1"] = { c:
[
	{ div:[""], c:
	[
		{ div:[], c:
		[			
			{ div:[""], case_vw_val_cat:["Case Category","",":v:cases:case_category"] },
			{ div:["tt"], case_vw_val:["Is Case GBV Related?",":v:cases:gbv_related::yesno:2"] },
		]},
		{ div:[], usub:["case_vw_sub_medical_exam,case_vw_sub_medical_exam","r_",":v:cases:case_category_fullname_id", CASE_CATEGORY_PHYSICAL_N_SEXUAL_ABUSE_ID] },
		{ div:[], usub:["case_vw_sub_incidence","r_",":v:cases:case_category_fullname_id", CASE_CATEGORY_SEXUAL_ABUSE_ID] },	
	]},
	{ div:["tt"], c:
	[
		{ s:["x tt v","Case Narrative"] },
		{ pre:["x y mh02 bd w60","",":v:cases:narrative"] }
	]},
	{ div:["tt"], c:
	[
		{ s:["x tt v","Case Plan"] },
		{ pre:["x y mh02 bd w60","",":v:cases:plan"] }
	]},
	
	{ div:[], usub:["case_vw_sub_justice","r_",":v:cases:case_category_fullname_id", CASE_CATEGORY_ABUSE_ID] },
		
	{ div:["tt"], c:
	[
		{ div:["c w17 r10"], case_vw_val:["Priority",":v:cases:priority::case_priority:1"] }, 
		{ div:["c w17 r10"], case_vw_val:["Status",":v:cases:status::case_status:1"] }, 
		{ div:["c w25"],  case_vw_val:["Escalated To",":v:cases:escalated_to"] },
		{ div:["e"] }
	]},
]};

te["case_vw_col_0"] = { c:
[
	{ div:[], c:
	[
		{ div:["t"], c:
		[
			{ s:["xx yy b n","Reported By"] },
			{ div:["e"] }
		]},
		{ u:["case_vw_reporter_r","reporters"] },
		
		{ u:["case_vw_reporter_uuid","reporters_uuid"] },
	]},

	{ p:["t15","clients"], c:
	[
		{ div:[], c:
		[
			{ s:["xx yy b n","Clients"] },
			{ div:["e"] }
		]},
		{ p:["","a"], u:["case_vw_client_r","clients"] },
	]},
	
	{ div:["t15","perpetrators"], c:
	[
		{ div:[], c:
		[
			{ s:["xx yy b n","Perpetrators"] },
			{ div:["e"] }
		]},
		{ p:["","a"], u:["case_vw_perpetrator_r","perpetrators"] },
	]},
	
	{ div:["t15","attachments"], c:
	[
		{ div:[], c:
		[
			{ s:["xx yy b n","Related Files"] },
			{ div:["e"] }
		]},
		{ p:["","a"], c:
		[
			{ s:["xx cd","None"] },
			{ u:["case_attachment_vw_r","attachments","","attachments"] },
		]}
	]},
	
	{ div:["tt"], c:
	[
		{ s:["xx tt cd","Services Offered"] },
		{ div:["x b05"], c:
		[ 
			{ uchk:["tagv",":v:cases:services","","",  "x y bd n gws_ mr"," %1"] }, 
			{ div:["e"] } 
		]},
		{ div:["bl2_b"], usub:["case_vw_sub_referals","r_",":v:cases:services",CASE_SERVICE_REFERAL_ID] },
		{ div:["bl2_b"], usub:["case_vw_sub_police_ref","r_",":v:cases:services",CASE_SERVICE_POLICE_ID] },
		{ div:["bl2_b"], usub:["case_vw_sub_other_service","r_",":v:cases:services",CASE_SERVICE_OTHER_ID] },

	]},
	
	{ div:["x yy"], case_vw_val_cat:["Know About 116","",":v:cases:knowabout116"] }
]};

te["case_vw_id_"] = { div:["section-to-print tt","ve"], c: 
[	
	{ div:["x20 y","vb"], c:
	[		
		{ div:["c x t02"], ac:["ay","","_uvw","h2 x y bd16 gb cw micon","arrow_back"] },	
		{ s:["c x08 tt h2 b",CASE_ID_PREFIX] },
		{ s:["c tt h2 b w40","%0"] },
		
		{ div:["d t r15","va"], c:
		[
			{ ac:["ao","","_print","x08 y h02 n gws_ cb",""], c:
			[
				{ s:["c micon h3","print"] },
				{ s:["c xx s","Print"] },
				{ div:["e"] }
			]}
		]},
				
		{ div:["d t r10 ","va"], c:
		[
			{ div:["w13","va"], s:["",""], c:
			[
				{ div:["c w10","va"], c:
				[
					{ ac:["ao mr_","case_update-cases_uuid-^","_vp","x08 y h02 n gws_ cb",""], c: 
					[
						{ s:["c micon h3","edit"] }, 
						{ s:["c xx s","Update"] }, 
						{ div:["e"], c:
						[ 
							{ arg:["",".id","-1"] }, 
							{ arg:["","case_id",":v:cases:id"] }, 
							{ u:["case_reporter_uuid_arg","reporters_uuid"] }
						]}
					]},
                			{ div:["g"], arg:["","","activity_case_ufn-cases-vf--@"] }
				]},
				{ ac:["c w03 ao","","_dd","x y h02 n gws_ cb",""], c:[ { div:["h02 w02 awb"] }] },
				{ div:["e"] }
			]},
			{ div:["dd w13 gws_ mt3","vdd"], c:
			[
				{ div:["","va"], ac:["ao","case_ed-cases_uuid-vf","_u","xx y cb",""], c: 
				[
					{ s:["","Edit"] },
					{ div:[], c:
					[ 
						{ arg:["",".id","-1"] }, 
						{ arg:["","case_id",":v:cases:id"] }, 
						{ u:["case_reporter_uuid_arg","reporters_uuid"] }
					]}
				]},
			]}
		]},

		{ div:["d t r10","va"],  c:
		[ 
			{ input:["g","","case_vw_id_t","1","radio"] },
			{ ac:["ao tab","","_tab","x08 y h02 n gws_ cb",""], c:
			[ 
				{ s:["c micon h3","history"] }, 
				{ s:["c xx s","Case History"] }, 
				{ div:["e"] } 
			]}
		]},

		{ div:["d t r10","va"], c:
		[ 
			{ input:["g","","case_vw_id_t","0","radio","1"] },
			{ ac:["ao tab","","_tab","x08 y gws_ h02 n cb",""], c:
			[ 
				{ s:["c micon h3","feed"] }, 
				{ s:["c xx s","Case Details"] }, 
				{ div:["e"] } 
			]}
		]},
		
		{ div:["e"] }
	]},

	{ div:["x25 tt"], c:[ { p:["c w100","nb"], c:[ { u:["nb","cases_nb"] }, { u:["nb","newcase_nb"] } ] }, { div:["e"] } ] },
		
	{ div:[], c:
	[
		{ div:[], c:
		[
			{ input:["g","","case_vw_id_v","0","radio","1"] },
			{ div:["tabv w130_ x20 t b30","ve"], c:
			[
				{ div:["c w45_ r50"], case_vw_col_0:[] },
				{ div:["c w75_"], case_vw_col_1:[] },
				{ p:["e","o"], c:[ { arg:["",".id","%0"] } ] } 
			]}
		]},
	
	 	{ div:[], c:
	 	[
			{ input:["g","","case_vw_id_v","1","radio"] },
	 		{ div:["tabv x30","vs"], u:["case_history","case_activities_ctx"] }
	 	]},
	 	
	 	{ div:["print-only"], c:
		[ 
			{ div:["page-break"] },
			{ u:["case_reporter_vw_id_print","reporters"] },
			{ u:["case_client_vw_id_print","clients"] },
			{ u:["case_perpetrator_vw_id_print","perpetrators"] },
			{ div:["x15","vs"], u:["case_history","case_activities_ctx"] }
	 	]}
	 	
	 ]}	
]};

te["case_vw_id"] = { case_vw_id_:[] };

// ------------------------------------------------------------------------

te["case_disability_root_id"] = { arg:["root_id_","",DISABILITY_ROOT_ID] };
te["case_school_level_root_id"] = { arg:["root_id_","",SCHOOL_LEVEL_ROOT_ID] };
te["case_school_type_root_id"] = { arg:["root_id_","",SCHOOL_TYPE_ROOT_ID] };
te["case_household_root_id"] = { arg:["root_id_","",HOUSEHOLD_TYPE_ROOT_ID] };
te["case_occupation_root_id"] = { arg:["root_id_","",EMPLOYMENT_STATUS_ROOT_ID] };
te["case_marital_root_id"] = { arg:["root_id_","",MARITAL_STATUS_ROOT_ID] };
te["case_hiv_root_id"] = { arg:["root_id_","",HIV_STATUS_ROOT_ID] };
te["case_health_root_id"] = { arg:["root_id_","",HEALTH_STATUS_ROOT_ID] };
te["case_shares_home_root_id"] = { arg:["root_id_","",SHARES_HOME_ROOT_ID] };
te["case_relationship_root_id"] = { arg:["root_id_","",RELATIONSHIP_ROOT_ID] };

te["case_tribe_root_id"] = { arg:["root_id_","",TRIBE_ROOT_ID] };
te["case_lang_root_id"] = { arg:["root_id_","",LANGUAGE_ROOT_ID] };
te["case_nationality_root_id"] = { arg:["root_id_","",NATIONALITY_ROOT_ID] };
te["case_national_id_type_root_id"] = { arg:["root_id_","",NATIONAL_ID_TYPE_ROOT_ID] };
te["case_location_root_id"] = { arg:["root_id_","",LOCATION_ROOT_ID] };
te["case_sex_root_id"] = { arg:["root_id_","",SEX_ROOT_ID] };
te["case_age_group_root_id"] = { arg:["root_id_","",AGE_GROUP_ROOT_ID] };

te["case_disposition_root_id"] = { arg:["root_id_","",DISPOSITION_ROOT_ID] };
te["case_referal_root_id"] = { arg:["root_id_","",CASE_REFERALS_ROOT_ID] };
te["case_service_root_id"] = { arg:["root_id_","",CASE_SERVICES_ROOT_ID] };
te["case_justice_root_id"] = { arg:["root_id_","",CASE_JUSTICE_ROOT_ID] };
te["case_assessment_root_id"] = { arg:["root_id_","",CASE_ASSESSMENT_ROOT_ID] };
te["case_category_root_id"] = { c:[ { arg:["root_id_","",CASE_CATEGORY_ROOT_ID] }, { arg:["sort","","fullname"] } ] };

te["case_location_level_root_id"] = { form:["tt"], c:
[
	{ input:["g","","level","0","radio","1"] },
	{ ac:["c opti l","","_optky","x y03","All"] },
	{ input:["g","level","level","1","radio"] },
	{ ac:["c opti l","","_optky","x y03","Region"] },
	{ input:["g","level","level","2","radio"] },
	{ ac:["c opti l","","_optky","x y03","District"] },
	{ input:["g","level","level","3","radio"] },
	{ ac:["c opti l","","_optky","x y03","County"] },
	{ input:["g","level","level","4","radio"] },
	{ ac:["c opti l","","_optky","x y03","Sub County"] },
	{ input:["g","level","level","5","radio"] },
	{ ac:["c opti l","","_optky","x y03","Parish"] },
	{ input:["g","level","level","6","radio"] },
	{ ac:["c opti l","","_optky","x y03","Village"] },
	{ input:["g","level","level","7","radio"] },
	{ ac:["c opti l","","_optky","x y03","Constituency"] },
	{ div:["e"], c:[ { arg:["root_id_","",LOCATION_ROOT_ID] }, { arg:["sort","","fullname"] } ] }
]};

te["case_category_level_root_id"] = { form:["tt"], c:
[
	{ input:["g","","level","0","radio","1"] },
	{ ac:["c opti l","","_optky","x y03","All"] },
	{ input:["g","level","level","1","radio"] },
	{ ac:["c opti l","","_optky","x y03","Case Type"] },
	{ input:["g","level","level","2","radio"] },
	{ ac:["c opti l","","_optky","x y03","Main Category"] },
	{ input:["g","level","level","3","radio"] },
	{ ac:["c opti l","","_optky","x y03","SubCategory 1"] },
	{ input:["g","level","level","4","radio"] },
	{ ac:["c opti l","","_optky","x y03","SubCategory 2"] },
	//{ input:["g","level","level","5","radio"] },
	//{ ac:["c opti l","","_optky","x y03","SubCategory 3"] },
	{ div:["e"], c:[ { arg:["root_id_","",CASE_CATEGORY_ROOT_ID] }, { arg:["sort","","fullname"] } ] }
]};

te["case_lc_main_root_id"] = { arg:["root_id_","",":k:subcategories_k:root_id_:2"] };
te["case_lc_main"] = { category_lc_main_:["case_lc_main_root_id"] };
te["case_location_lc_main"] = { category_lc_main_:["case_location_level_root_id"] };
te["case_category_lc_main"] = { category_lc_main_:["case_category_level_root_id"] };

// ------------------------------------------------------------------------

te["case_f_tags_"] = { c: 
[

	{ f:["CaseID",null,		" %0","id",""] },
	{ f:["Created On",null,		" :d:dmy:0: ","created_on",""] },
	{ f:["Created By",null,		" %1","created_by_id"," %1"] },
	{ f:["Source",null,		" %0","src",""] },
	{ f:["Category",null,		" %1","case_category_id"," %1"] },
        { f:["GBV Related",null,        " ::yesno:0:2","gbv_related",""] },
	{ f:["Priority",null,		" ::case_priority:0:1","priority",""] },
	{ f:["Status",null,		" ::case_status:0:1","status",""] },
	{ f:["Escalated To",null,	" %1","escalated_to_id"," %1"] },
	{ f:["Case Assessment",null,	" %1","assessment_id"," %1"] },
	{ f:["State of the Case in the Justice System",null," %1","justice_id"," %1"] },
	
	{ f:["Reporter Name",null,	" %0","reporter_fullname",""] },
	{ f:["Reporter Phone",null,	" %0","reporter_phone",""] },
	{ f:["Reporter Age",null,	" %1","reporter_age_group_id"," %1"] },
	{ f:["Reporter Gender",null,	" %1","reporter_sex_id"," %1"] },
	{ f:["Reporter Location",null,	" %1","reporter_location_id"," %1"] },
	{ f:["Reporter ID Type",null,	" %1","reporter_national_id_type_id"," %1"] },
	{ f:["Reporter Nationality",null," %1","reporter_nationality_id"," %1"] },
	{ f:["Reporter Language",null,	" %1","reporter_lang_id"," %1"] },
	{ f:["Reporter Tribe",null,	" %1","reporter_tribe_id"," %1"] },	

	{ f:["Client Name",null,	" %0","clients^contact_fullname",""] },
	{ f:["Client Phone",null,	" %0","clients^contact_phone",""] },
	{ f:["Client Age",null,		" %1","clients^contact_age_group_id"," %1"] },
	{ f:["Client Gender",null,	" %1","clients^contact_sex_id"," %1"] },
	{ f:["Client Location",null,	" %1","clients^contact_location_id"," %1"] },
	{ f:["Client ID Type",null,	" %1","clients^contact_national_id_type_id"," %1"] },
	{ f:["Client Nationality",null,	" %1","clients^contact_nationality_id"," %1"] },
	{ f:["Client Language",null,	" %1","clients^contact_lang_id"," %1"] },
	{ f:["Client Tribe",null,	" %1","clients^contact_tribe_id"," %1"] },
	{ f:["Reporter Relationship to Client",null,	" %1","clients^relationship_id"," %1"] },
	{ f:["Client Health Status",null,	" %1","clients^health_id"," %1"] },
	{ f:["Client HIV Status",null,		" %1","clients^hiv_id"," %1"] },
	{ f:["Client Marital Status",null,	" %1","clients^marital_id"," %1"] },
	{ f:["Client Spouse Profession",null,	" %1","clients^spouse_profession_id"," %1"] },
	{ f:["Client Household Type",null,	" %1","clients^household_id"," %1"] },
	{ f:["Client Head of Household Occupation",null,	" %1","clients^household_head_occupation_id"," %1"] },
	{ f:["Client Parent/Guardian Marital Status",null,	" %1","clients^guardian_marital_id"," %1"] },
	{ f:["Client School Level",null,	" %1","clients^school_level_id"," %1"] },
	{ f:["Client School Type",null,		" %1","clients^school_type_id"," %1"] },
        { f:["Client Disability",null,    	" %1","clients^disability_id"," %1"] },

	{ f:["Perp Name",null,		" %0","perpetrators^contact_fullname",""] },
	{ f:["Perp Phone",null,		" %0","perpetrators^contact_phone",""] },
	{ f:["Perp Age",null,		" %1","perpetrators^contact_age_group_id"," %1"] },
	{ f:["Perp Gender",null,	" %1","perpetrators^contact_sex_id"," %1"] },
	{ f:["Perp Location",null,	" %1","perpetrators^contact_location_id"," %1"] },
	{ f:["Perp ID Type",null,	" %1","perpetrators^contact_national_id_type_id"," %1"] },
	{ f:["Perp Nationality",null,	" %1","perpetrators^contact_nationality_id"," %1"] },
	{ f:["Perp Language",null,	" %1","perpetrators^contact_lang_id"," %1"] },
	{ f:["Perp Tribe",null,		" %1","perpetrators^contact_tribe_id"," %1"] },
	{ f:["Perp Relationship to Client",null,	" %1","perpetrators^relationship_id"," %1"] },
	{ f:["Perp Shares Home with Client",null,	" %1","perpetrators^shareshome_id"," %1"] },
	{ f:["Perp Health Status",null,			" %1","perpetrators^health_id"," %1"] },
	{ f:["Perp Marital Status",null,		" %1","perpetrators^marital_id"," %1"] },
	{ f:["Perp Profession",null,			" %1","perpetrators^employment_id"," %1"] },
	{ f:["Perp Spouse's Profession",null,		" %1","perpetrators^spouse_profession_id"," %1"] },

	{ f:["Services",null,		" %1","services^category_id"," %1"] },
	
	{ f:["Referals",null,		" %1","referals^category_id"," %1"] },
		
	{ p:["g","o"], arg:["","_title",null] }, 
	{ div:["e"] }
]};

te["case_f_tags_k"] = { case_f_tags_:[":k:cases_k:id:2", ":k:cases_k:created_on:2", ":k:cases_k:created_by_id:2", ":k:cases_k:src:2", 
":k:cases_k:case_category_id:2",":k:cases_k:gbv_related:2", ":k:cases_k:priority:2", ":k:cases_k:status:2", ":k:cases_k:escalated_to_id:2", 
":k:cases_k:assessment_id:2",  ":k:cases_k:justice_id:2",  

":k:cases_k:reporter_fullname:2", ":k:cases_k:reporter_phone:2", 
":k:cases_k:reporter_age_group_id:2", ":k:cases_k:reporter_sex_id:2", ":k:cases_k:reporter_location_id:2",
":k:cases_k:reporter_national_id_type_id:2", ":k:cases_k:reporter_nationality_id:2", ":k:cases_k:reporter_lang_id:2", ":k:cases_k:reporter_tribe_id:2",

":k:cases_k:clients^contact_fullname:2", ":k:cases_k:clients^contact_phone:2", 
":k:cases_k:clients^contact_age_group_id:2", ":k:cases_k:clients^contact_sex_id:2", ":k:cases_k:clients^contact_location_id:2", 
":k:cases_k:clients^contact_national_id_type_id:2", ":k:cases_k:clients^contact_nationality_id:2", ":k:cases_k:clients^contact_lang_id:2",
":k:cases_k:clients^contact_tribe_id:2",
":k:cases_k:clients^relationship_id:2",
":k:cases_k:clients^health_id:2", ":k:cases_k:clients^hiv_id:2", ":k:cases_k:clients^marital_id:2",
":k:cases_k:clients^spouse_profession_id:2", ":k:cases_k:clients^household_id:2", ":k:cases_k:clients^household_head_occupation_id:2",
":k:cases_k:clients^guardian_marital_id:2", ":k:cases_k:clients^school_level_id:2", ":k:cases_k:clients^school_type_id:2",
":k:cases_k:clients^disability_id:2",

":k:cases_k:perpetrators^contact_fullname:2", ":k:cases_k:perpetrators^contact_phone:2", 
":k:cases_k:perpetrators^contact_age_group_id:2", ":k:cases_k:perpetrators^contact_sex_id:2", ":k:cases_k:perpetrators^contact_location_id:2",
":k:cases_k:perpetrators^contact_national_id_type_id:2", ":k:cases_k:perpetrators^contact_nationality_id:2", ":k:cases_k:perpetrators^contact_lang_id:2",
":k:cases_k:perpetrators^contact_tribe_id:2",
":k:cases_k:perpetrators^relationship_id:2", 
":k:cases_k:perpetrators^shareshome_id:2", ":k:cases_k:perpetrators^health_id:2",  ":k:cases_k:perpetrators^marital_id:2",
":k:cases_k:perpetrators^employment_id:2", ":k:cases_k:perpetrators^spouse_profession_id:2", 

":k:cases_k:services^category_id:2",

":k:cases_k:referals^category_id:2",
"%5"] }; 

te["case_f_tags"] = { case_f_tags_:[":k:cases_f:id", ":k:cases_f:created_on", ":k:cases_f:created_by_id", ":k:cases_f:src", 
":k:cases_f:case_category_id", ":k:cases_f:gbv_related", ":k:cases_f:priority", ":k:cases_f:status", ":k:cases_f:escalated_to_id",  
":k:cases_f:assessment_id",  ":k:cases_f:justice_id",  

":k:cases_f:reporter_fullname", ":k:cases_f:reporter_phone", 
":k:cases_f:reporter_age_group_id", ":k:cases_f:reporter_sex_id", ":k:cases_f:reporter_location_id",
":k:cases_f:reporter_national_id_type_id", ":k:cases_f:reporter_nationality_id", ":k:cases_f:reporter_lang_id", ":k:cases_f:reporter_tribe_id",

":k:cases_f:clients^contact_fullname", ":k:cases_f:clients^contact_phone", 
":k:cases_f:clients^contact_age_group_id", ":k:cases_f:clients^contact_sex_id", ":k:cases_f:clients^contact_location_id",
":k:cases_f:clients^contact_national_id_type_id", ":k:cases_f:clients^contact_nationality_id", ":k:cases_f:clients^contact_lang_id",
":k:cases_f:clients^contact_tribe_id",
":k:cases_f:clients^relationship_id",
":k:cases_f:clients^health_id", ":k:cases_f:clients^hiv_id", ":k:cases_f:clients^marital_id",
":k:cases_f:clients^spouse_profession_id", ":k:cases_f:clients^household_id", ":k:cases_f:clients^household_head_occupation_id",
":k:cases_f:clients^guardian_marital_id", ":k:cases_f:clients^school_level_id", ":k:cases_f:clients^school_type_id",
":k:cases_f:clients^disability_id",

":k:cases_f:perpetrators^contact_fullname", ":k:cases_f:perpetrators^contact_phone", 
":k:cases_f:perpetrators^contact_age_group_id", ":k:cases_f:perpetrators^contact_sex_id", ":k:cases_f:perpetrators^contact_location_id",
":k:cases_f:perpetrators^contact_national_id_type_id", ":k:cases_f:perpetrators^contact_nationality_id", ":k:cases_f:perpetrators^contact_lang_id",
":k:cases_f:perpetrators^contact_tribe_id",
":k:cases_f:perpetrators^relationship_id",
":k:cases_f:perpetrators^shareshome_id", ":k:cases_f:perpetrators^health_id",  ":k:cases_f:perpetrators^marital_id",
":k:cases_f:perpetrators^employment_id", ":k:cases_f:perpetrators^spouse_profession_id", 

":k:cases_f:services^category_id",
":k:cases_f:referals^category_id",
":k:cases_f:_title"] };

te["case_referals_f"] = { c:
[
	{ div:["xx yy"], kf_l:["Referals","tag_-r_--o--%1-category_id-referals^category_id-%0-%1", "case_lc_main-subcategories",
":k:cases_f:referals^category_id", ""," %1","category_id","referals^category_id"," %0"," %1", "case_referal_root_id"] },
]};

te["case_services_f"] = { c:
[
	{ div:["xx yy"], kf_l:["Services","tag_-r_--o--%1-category_id-services^category_id-%0-%1", "case_lc_main-subcategories", 
":k:cases_f:services^category_id", ""," %1","category_id","services^category_id"," %0"," %1", "case_service_root_id"] },
]};

te["case_perpetrators_f"] = { c:
[
	{ div:["xx yy"], kf_s:["Name","perpetrators^contact_fullname",":k:cases_f:perpetrators^contact_fullname"] },
	{ div:["xx yy"], kf_s:["Phone","perpetrators^contact_phone",":k:cases_f:perpetrators^contact_phone"] },
	
	{ div:["xx yy"], kf_l:["Age","tag_-r_--o--%1-category_id-perpetrators^contact_age_group_id-%0-%1", "case_lc_main-subcategories", 
":k:cases_f:perpetrators^contact_age_group_id", ""," %1","category_id","perpetrators^contact_age_group_id"," %0"," %1", "case_age_group_root_id"] },

	{ div:["xx yy"], kf_l:["Sex","tag_-r_--o--%1-category_id-perpetrators^contact_sex_id-%0-%1", "case_lc_main-subcategories",  
":k:cases_f:perpetrators^contact_sex_id", ""," %1","category_id","perpetrators^contact_sex_id"," %0"," %1", "case_sex_root_id"] },
	{ div:["xx yy"], kf_l:["Location","tag_-r_--o--%1-category_id-perpetrators^contact_location_id-%0-%1", "case_location_lc_main-subcategories",  ":k:cases_f:perpetrators^contact_location_id", ""," %1","category_id","perpetrators^contact_location_id"," %0"," %1", "case_location_root_id"] },

	{ div:["xx yy"], kf_l:["ID Type","tag_-r_--o--%1-category_id-perpetrators^contact_national_id_type_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:perpetrators^contact_national_id_type_id", ""," %1","category_id","perpetrators^contact_national_id_type_id"," %0"," %1", "case_national_id_type_root_id"] },

	{ div:["xx yy"], kf_l:["Nationality","tag_-r_--o--%1-category_id-perpetrators^contact_nationality_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:perpetrators^contact_nationality_id", ""," %1","category_id","perpetrators^contact_nationality_id"," %0"," %1", "case_nationality_root_id"] },

	{ div:["xx yy"], kf_l:["Language","tag_-r_--o--%1-category_id-perpetrators^contact_lang_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:perpetrators^contact_lang_id", ""," %1","category_id","perpetrators^contact_lang_id"," %0"," %1", "case_lang_root_id"] },

	{ div:["xx yy"], kf_l:["Tribe","tag_-r_--o--%1-category_id-perpetrators^contact_tribe_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:perpetrators^contact_tribe_id", ""," %1","category_id","perpetrators^contact_tribe_id"," %0"," %1", "case_tribe_root_id"] },

	{ div:["xx yy"], kf_l:["Perpetrator's Relationship to Client","tag_-r_--o--%1-category_id-perpetrators^relationship_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:perpetrators^relationship_id", ""," %1","category_id","perpetrators^relationship_id"," %0"," %1", "case_relationship_root_id"] },

	{ div:["xx yy"], kf_l:["Shares Home with Client","tag_-r_--o--%1-category_id-perpetrators^shareshome_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:perpetrators^shareshome_id", ""," %1","category_id","perpetrators^shareshome_id"," %0"," %1", "case_shares_home_root_id"] },

	{ div:["xx yy"], kf_l:["Health Status","tag_-r_--o--%1-category_id-perpetrators^health_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:perpetrators^health_id", ""," %1","category_id","perpetrators^health_id"," %0"," %1", "case_health_root_id"] },

	{ div:["xx yy"], kf_l:["Marital Status","tag_-r_--o--%1-category_id-perpetrators^marital_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:perpetrators^marital_id", ""," %1","category_id","perpetrators^marital_id"," %0"," %1", "case_marital_root_id"] },

	{ div:["xx yy"], kf_l:["Perpetrator's Profession","tag_-r_--o--%1-category_id-perpetrators^employment_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:perpetrators^employment_id", ""," %1","category_id","perpetrators^employment_id"," %0"," %1", "case_occupation_root_id"] },

	{ div:["xx yy"], kf_l:["Perpetrator's Spouse Profession","tag_-r_--o--%1-category_id-perpetrators^spouse_profession_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:perpetrators^spouse_profession_id", ""," %1","category_id","perpetrators^spouse_profession_id"," %0"," %1", "case_occupation_root_id"] },

]};

te["case_clients_f"] = { c:
[
	{ div:["xx yy"], kf_s:["Name","clients^contact_fullname",":k:cases_f:clients^contact_fullname"] },
	{ div:["xx yy"], kf_s:["Phone","clients^contact_phone",":k:cases_f:clients^contact_phone"] },

	{ div:["xx yy"], kf_l:["Age","tag_-r_--o--%1-category_id-clients^contact_age_group_id-%0-%1", "case_lc_main-subcategories", 
":k:cases_f:clients^contact_age_group_id", ""," %1","category_id","clients^contact_age_group_id"," %0"," %1", "case_age_group_root_id"] },

	{ div:["xx yy"], kf_l:["Sex","tag_-r_--o--%1-category_id-clients^contact_sex_id-%0-%1", "case_lc_main-subcategories",  
":k:cases_f:clients^contact_sex_id", ""," %1","category_id","clients^contact_sex_id"," %0"," %1", "case_sex_root_id"] },

	{ div:["xx yy"], kf_l:["Location","tag_-r_--o--%1-category_id-clients^contact_location_id-%0-%1", "case_location_lc_main-subcategories",  ":k:cases_f:clients^contact_location_id", ""," %1","category_id","clients^contact_location_id"," %0"," %1", "case_location_root_id"] },

	{ div:["xx yy"], kf_l:["ID Type","tag_-r_--o--%1-category_id-clients^contact_national_id_type_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:clients^contact_national_id_type_id", ""," %1","category_id","clients^contact_national_id_type_id"," %0"," %1", "case_national_id_type_root_id"] },

	{ div:["xx yy"], kf_l:["Nationality","tag_-r_--o--%1-category_id-clients^contact_nationality_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:clients^contact_nationality_id", ""," %1","category_id","clients^contact_nationality_id"," %0"," %1", "case_nationality_root_id"] },

	{ div:["xx yy"], kf_l:["Language","tag_-r_--o--%1-category_id-clients^contact_lang_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:clients^contact_lang_id", ""," %1","category_id","clients^contact_lang_id"," %0"," %1", "case_lang_root_id"] },

	{ div:["xx yy"], kf_l:["Tribe","tag_-r_--o--%1-category_id-clients^contact_tribe_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:clients^contact_tribe_id", ""," %1","category_id","clients^contact_tribe_id"," %0"," %1", "case_tribe_root_id"] },

	{ div:["xx yy"], kf_l:["Reporter Relationship to Client","tag_-r_--o--%1-category_id-clients^relationship_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:clients^relationship_id", ""," %1","category_id","clients^relationship_id"," %0"," %1", "case_relationship_root_id"] },

	{ div:["xx yy"], kf_l:["Health Status","tag_-r_--o--%1-category_id-clients^health_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:clients^health_id", ""," %1","category_id","clients^health_id"," %0"," %1", "case_health_root_id"] },

	{ div:["xx yy"], kf_l:["HIV Status","tag_-r_--o--%1-category_id-clients^hiv_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:clients^hiv_id", ""," %1","category_id","clients^hiv_id"," %0"," %1", "case_hiv_root_id"] },

	{ div:["xx yy"], kf_l:["Marital Status","tag_-r_--o--%1-category_id-clients^marital_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:clients^marital_id", ""," %1","category_id","clients^marital_id"," %0"," %1", "case_marital_root_id"] },

	{ div:["xx yy"], kf_l:["Client's Spouse Profession","tag_-r_--o--%1-category_id-clients^spouse_profession_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:clients^spouse_profession_id", ""," %1","category_id","clients^spouse_profession_id"," %0"," %1", "case_occupation_root_id"] },

	{ div:["xx yy"], kf_l:["Household Type","tag_-r_--o--%1-category_id-clients^household_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:clients^household_id", ""," %1","category_id","clients^household_id"," %0"," %1", "case_household_root_id"] },

	{ div:["xx yy"], kf_l:["Head of Household Occupation","tag_-r_--o--%1-category_id-clients^household_head_occupation_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:clients^household_head_occupation_id", ""," %1","category_id","clients^household_head_occupation_id"," %0"," %1", "case_occupation_root_id"] },

	{ div:["xx yy"], kf_l:["Parent/Guardian Marital Status","tag_-r_--o--%1-category_id-clients^guardian_marital_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:clients^guardian_marital_id", ""," %1","category_id","clients^guardian_marital_id"," %0"," %1", "case_marital_root_id"] },

	{ div:["xx yy"], kf_l:["School Level","tag_-r_--o--%1-category_id-clients^school_level_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:clients^school_level_id", ""," %1","category_id","clients^school_level_id"," %0"," %1", "case_school_level_root_id"] },

	{ div:["xx yy"], kf_l:["School Type","tag_-r_--o--%1-category_id-clients^school_type_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:clients^school_type_id", ""," %1","category_id","clients^school_type_id"," %0"," %1", "case_school_type_root_id"] },
	
	 { div:["xx yy"], kf_l:["Client Disability","tag_-r_--o--%1-category_id-clients^disability_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:clients^disability_id", ""," %1","category_id","clients^disability_id"," %0"," %1", "case_disability_root_id"] },
]};

te["case_reporters_f"] = { c:
[
	{ div:["xx yy"], kf_s:["Name","reporter_fullname",":k:cases_f:reporter_fullname"] },
	{ div:["xx yy"], kf_s:["Phone","reporter_phone",":k:cases_f:reporter_phone"] },
	{ div:["xx yy"], kf_l:["Age","tag_-r_--o--%1-category_id-reporter_age_group_id-%0-%1", "case_lc_main-subcategories", 
":k:cases_f:reporter_age_group_id", ""," %1","category_id","reporter_age_group_id"," %0"," %1", "case_age_group_root_id"] },
	{ div:["xx yy"], kf_l:["Sex","tag_-r_--o--%1-category_id-reporter_sex_id-%0-%1", "case_lc_main-subcategories",  
":k:cases_f:reporter_sex_id", ""," %1","category_id","reporter_sex_id"," %0"," %1", "case_sex_root_id"] },
	{ div:["xx yy"], kf_l:["Location","tag_-r_--o--%1-category_id-reporter_location_id-%0-%1", "case_location_lc_main-subcategories",  ":k:cases_f:reporter_location_id", ""," %1","category_id","reporter_location_id"," %0"," %1", "case_location_root_id"] },

	{ div:["xx yy"], kf_l:["ID Type","tag_-r_--o--%1-category_id-reporter_national_id_type_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:reporter_national_id_type_id", ""," %1","category_id","reporter_national_id_type_id"," %0"," %1", "case_national_id_type_root_id"] },

	{ div:["xx yy"], kf_l:["Nationality","tag_-r_--o--%1-category_id-reporter_nationality_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:reporter_nationality_id", ""," %1","category_id","reporter_nationality_id"," %0"," %1", "case_nationality_root_id"] },

	{ div:["xx yy"], kf_l:["Language","tag_-r_--o--%1-category_id-reporter_lang_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:reporter_lang_id", ""," %1","category_id","reporter_lang_id"," %0"," %1", "case_lang_root_id"] },

	{ div:["xx yy"], kf_l:["Tribe","tag_-r_--o--%1-category_id-reporter_tribe_id-%0-%1", "case_lc_main-subcategories",  ":k:cases_f:reporter_tribe_id", ""," %1","category_id","reporter_tribe_id"," %0"," %1", "case_tribe_root_id"] },

]};

te["case_cases_f"] = { c:
[
	{ div:["xx yy"], kf_s:["CaseID","id",":k:cases_f:id"] },			
			
	{ div:["xx yy"], kf_d:["Created On"," :d:dmy:0: ","created_on",":k:cases_f:created_on","created_on",":k:cases_f:created_on"] },
			
	{ div:["xx yy"], kf_l:["Created By","tag_-r_--o--%5-user_id-created_by_id-%0-%5",   "user_lc_main-users",":k:cases_f:created_by_id", 
""," %1","user_id","created_by_id"," %0"," %1",  "noop"] },

	{ div:["xx yy"], kf_c:["Source","tag_-r_--o--::case_src:0:1--src-%0-",  	":k:cases_f:src",
""," %0","","src"," %0","", 				":k:cases_f:src","case_src", "src"," %0",""] },
		
	{ div:["xx yy"], kf_l:["Category","tag_-r_--o--%1-category_id-case_category_id-%0-%1",   "case_category_lc_main-subcategories",  ":k:cases_f:case_category_id",  ""," %1","category_id","case_category_id"," %0"," %1", "case_category_root_id"] },
	
	 { div:["xx yy"], kf_c:["GBV Related", "tag_-r_--o--::yesno:0:2--gbv_related-%0-",  ":k:cases_f:gbv_related",
""," ::yesno:0:2","","gbv_related"," %0","",       ":k:cases_f:gbv_related","yesno",  "gbv_related"," ::yesno:0:2",""] },

	{ div:["xx yy"], kf_c:["Priority", "tag_-r_--o--::case_priority:0:1--priority-%0-",  ":k:cases_f:priority", 
""," ::case_priority:0:1","","priority"," %0","", 	":k:cases_f:priority","case_priority",  "priority"," ::case_priority:0:1",""] },
				
	{ div:["xx yy"], kf_c:["Status", "tag_-r_--o--::case_status:0:1--status-%0-",  	":k:cases_f:status",
""," ::case_status:0:1","","status"," %0","", 	":k:cases_f:status","case_status",  "status"," ::case_status:0:1",""] },
		
	{ div:["xx yy"], kf_l:["Escalated To","tag_-r_--o--%5-user_id-escalated_to_id-%0-%5",   "user_lc_main-users", ":k:cases_f:escalated_to_id", 
""," %1","user_id","escalated_to_id"," %0"," %1", "noop"] },	
		
	{ div:["xx yy"], kf_l:["Case Assessment","tag_-r_--o--%1-category_id-assessment_id-%0-%1",   "case_lc_main-subcategories", ":k:cases_f:assessment_id", 
""," %1","category_id","assessment_id"," %0"," %1", "case_assessment_root_id"] },	

	{ div:["xx yy"], kf_l:["Status in Justice System","tag_-r_--o--%1-category_id-justice_id-%0-%1",   "case_lc_main-subcategories", ":k:cases_f:justice_id", 
""," %1","category_id","justice_id"," %0"," %1", "case_justice_root_id"] },	
	
				
]};
	
te["case_f"] = { div:["w55 ma sh__ y gw_","vddvf"], ev:["_undd"], c:
[
	{ s:["x20 t15 n b","Search Case"] },
	{ div:[], c:
	[
		{ div:["xx t15 bb_","vb"], c:
		[
			{ div:["c x"], c:[ { input:["g","","case_f_vw_t","0","radio","1"] }, { ac:["ay tabu","","_tab","xx y cb","Case"] } ] },
			{ div:["c x"], c:[ { input:["g","","case_f_vw_t","1","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Reporter"] } ] },
			{ div:["c x"], c:[ { input:["g","","case_f_vw_t","2","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Client"] } ] },
			{ div:["c x"], c:[ { input:["g","","case_f_vw_t","3","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Perpetrator"] } ] },
			{ div:["c x"], c:[ { input:["g","","case_f_vw_t","4","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Sevices"] } ] },
			{ div:["c x"], c:[ { input:["g","","case_f_vw_t","5","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Referals"] } ] },
			{ div:["e"] }
		]},
		{ div:["x15 tt b20"], c:
		[
			{ div:[], c:[ { input:["g","","case_f_vw_tv","0","radio","1"] }, { div:["tabv"], case_cases_f:[] } ] },
			{ div:[], c:[ { input:["g","","case_f_vw_tv","1","radio"] }, { div:["tabv"], case_reporters_f:[] } ] },
			{ div:[], c:[ { input:["g","","case_f_vw_tv","2","radio"] }, { div:["tabv"], case_clients_f:[] } ] },
			{ div:[], c:[ { input:["g","","case_f_vw_tv","3","radio"] }, { div:["tabv"], case_perpetrators_f:[] } ] },
			{ div:[], c:[ { input:["g","","case_f_vw_tv","4","radio"] }, { div:["tabv"], case_services_f:[] } ] },
			{ div:[], c:[ { input:["g","","case_f_vw_tv","5","radio"] }, { div:["tabv"], case_referals_f:[] } ] }
		]}
	]},
	{ p:["g","o"], arg:["","_title",":k:cases_f:_title"] },
	{ vp_apply:["case_f_tags-cases_f"] }
]};

// ------------------------------------------------------------------------

te["case_footer"] = { div:["x gw ba"], c:
[
	{ div:["d y07"], pg:["pgto","case_list-cases"," dh","da dl","case_list-cases"," dh","da dr"] },
	{ div:["e"] }
]};

te["case_r"] = { div:[], c: 
[
	{ input:["g","","casevwr","1","radio",""] },
	{ ac:["ay w300","case_vw_id-cases-@","_vw","cb gw",""], c:
	[
		{ div:["c w07"], s:["tt b05 h01_  xx","%0"] },
		{ div:["c w10"], s:["tt b05 h01_  xx","%2"] },
		{ div:["c w16"], s:["tt b05 h01_  xx",":d:dmyhnr:1: "] },
		{ div:["c w10"], s:["tt b05 h01_ xx",":v:cases:src"] },
		{ div:["c w45"], s:["tt b05 xx",""], uval:["",":v:cases:case_category"] }, // category
                { div:["c w10"], s:["tt b05 h01_  xx",":v:cases:gbv_related::yesno:2"] },
		{ div:["c w10"], s:["tt b05 h01_  xx",":v:cases:priority::case_priority:1"] },
		{ div:["c w08"], s:["tt b05 h01_  xx",":v:cases:status::case_status:2"] },
		{ div:["c w12"], s:["tt b05 h01_  xx",":v:cases:escalated_to"] },
		{ div:["c w12"], s:["tt b05   xx",""], uval:["",":v:cases:assessment"] },
		{ div:["c w12"], s:["tt b05   xx",""], uval:["",":v:cases:justice"] },

		{ div:["c w30"], s:["tt b05 xx",""], c:
		[
			{ s:["c",":v:cases:reporter_fullname"] },
			{ s:["c",","] },
			{ div:["c l"], uval:["",":v:cases:reporter_sex"] },
			{ s:["c",","] },
			{ div:["c l"], uval:["",":v:cases:reporter_age_group"] },
			{ div:["e"] }
		]},
		{ div:["c w100"], s:["tt b05 xx",""], uval:["",":v:cases:reporter_location"] },
		{ div:["e"], arg:["",".id","%0"] }
	]}
]};


te["case_k"] = { div:["w300 bt bb"], s:["",""], c: // activate filter ctx
[
	{ k_a:["c w07","case_rr-cases","cd st","Case ID","da db","id",":k:cases_k:id:2"] },
	{ k_a:["c w10","case_rr-cases","cd st","Created By","da db","created_by_id",":k:cases_k:created_by_id:2"] },
	{ k_a:["c w16","case_rr-cases","cd st","Created On","da db","created_on",":k:cases_k:created_on:2"] },
	{ k_a:["c w10","case_rr-cases","cd","Source","da db","src",":k:cases_k:src:2"] },
	{ k_a:["c w45","case_rr-cases","cd st","Category","da db","case_category_id",":k:cases_k:case_category_id:2"] },
	{ k_a:["c w10","case_rr-cases","cd","GBV","da db","gbv_related",":k:cases_k:gbv_related:2"] },

	{ k_a:["c w10","case_rr-cases","cd","Priority","da db","priority",":k:cases_k:priority:2"] },
	{ k_a:["c w08","case_rr-cases","cd","Status","da db","status",":k:cases_k:status:2"] },
	{ k_a:["c w12","case_rr-cases","cd","Escalated To","da db","escalated_to_id",":k:cases_k:escalated_to_id:2"] },
	{ k_a:["c w12","case_rr-cases","cd","Assessment","da db","assessment_id",":k:cases_k:assessment_id:2"] },
	{ k_a:["c w12","case_rr-cases","cd","Justice Status","da db","justice_id",":k:cases_k:justice_id:2"] },
	{ k_a:["c w30","case_rr-cases","cd","Reporter","da db","reporter_phone",":k:cases_k:reporter_phone:2"] },
	{ k_a:["c w50","case_rr-cases","cd","Reporter Location","da db","",""] },
	{ div:["e"], c:
	[

{ arg:["","reporter_contact_id",":k:cases_k:reporter_contact_id:2"] },
{ arg:["","reporter_fullname",":k:cases_k:reporter_fullname:2"] },
{ arg:["","reporter_phone",":k:cases_k:reporter_phone:2"] },
{ arg:["","reporter_age_group_id",":k:cases_k:reporter_age_group_id:2"] },
{ arg:["","reporter_sex_id",":k:cases_k:reporter_sex_id:2"] },
{ arg:["","reporter_location_id",":k:cases_k:reporter_location_id:2"] },
{ arg:["","reporter_national_id_type_id",":k:cases_k:reporter_national_id_type_id:2"] },
{ arg:["","reporter_nationality_id",":k:cases_k:reporter_nationality_id:2"] },
{ arg:["","reporter_lang_id",":k:cases_k:reporter_lang_id:2"] },
{ arg:["","reporter_tribe_id",":k:cases_k:reporter_tribe_id:2"] },

{ arg:["","clients^contact_fullname",":k:cases_k:clients^contact_fullname:2"] },
{ arg:["","clients^contact_phone",":k:cases_k:clients^contact_phone:2"] },
{ arg:["","clients^contact_age_group_id",":k:cases_k:clients^contact_age_group_id:2"] },
{ arg:["","clients^contact_sex_id",":k:cases_k:clients^contact_sex_id:2"] },
{ arg:["","clients^contact_location_id",":k:cases_k:clients^contact_location_id:2"] },
{ arg:["","clients^contact_national_id_type_id",":k:cases_k:clients^contact_national_id_type_id:2"] },
{ arg:["","clients^contact_nationality_id",":k:cases_k:clients^contact_nationality_id:2"] },
{ arg:["","clients^contact_lang_id",":k:cases_k:clients^contact_lang_id:2"] },
{ arg:["","clients^contact_tribe_id",":k:cases_k:clients^contact_tribe_id:2"] },
{ arg:["","clients^relationship_id",":k:cases_k:clients^relationship_id:2"] },
{ arg:["","clients^health_id",":k:cases_k:clients^health_id:2"] },
{ arg:["","clients^hiv_id",":k:cases_k:clients^hiv_id:2"] },
{ arg:["","clients^marital_id",":k:cases_k:clients^marital_id:2"] },
{ arg:["","clients^spouse_profession_id",":k:cases_k:clients^spouse_profession_id:2"] },
{ arg:["","clients^household_id",":k:cases_k:clients^household_id:2"] },
{ arg:["","clients^household_head_occupation_id",":k:cases_k:clients^household_head_occupation_id:2"] },
{ arg:["","clients^guardian_marital_id",":k:cases_k:clients^guardian_marital_id:2"] },
{ arg:["","clients^school_level_id",":k:cases_k:clients^school_level_id:2"] },
{ arg:["","clients^school_type_id",":k:cases_k:clients^school_type_id:2"] },

{ arg:["","perpetrators^contact_fullname",":k:cases_k:perpetrators^contact_fullname:2"] },
{ arg:["","perpetrators^contact_phone",":k:cases_k:perpetrators^contact_phone:2"] },
{ arg:["","perpetrators^contact_age_group_id",":k:cases_k:perpetrators^contact_age_group_id:2"] },
{ arg:["","perpetrators^contact_sex_id",":k:cases_k:perpetrators^contact_sex_id:2"] },
{ arg:["","perpetrators^contact_location_id",":k:cases_k:perpetrators^contact_location_id:2"] },
{ arg:["","perpetrators^contact_national_id_type_id",":k:cases_k:perpetrators^contact_national_id_type_id:2"] },
{ arg:["","perpetrators^contact_nationality_id",":k:cases_k:perpetrators^contact_nationality_id:2"] },
{ arg:["","perpetrators^contact_lang_id",":k:cases_k:perpetrators^contact_lang_id:2"] },
{ arg:["","perpetrators^contact_tribe_id",":k:cases_k:perpetrators^contact_tribe_id:2"] },
{ arg:["","perpetrators^relationship_id",":k:cases_k:perpetrators^relationship_id:2"] },
{ arg:["","perpetrators^shareshome_id",":k:cases_k:perpetrators^shareshome_id:2"] },
{ arg:["","perpetrators^health_id",":k:cases_k:perpetrators^health_id:2"] },
{ arg:["","perpetrators^marital_id",":k:cases_k:perpetrators^marital_id:2"] },
{ arg:["","perpetrators^employment_id",":k:cases_k:perpetrators^employment_id:2"] },
{ arg:["","perpetrators^spouse_profession_id",":k:cases_k:perpetrators^spouse_profession_id:2"] },

{ arg:["","referals^category_id",":k:cases_k:referals^category_id:2"] },

{ arg:["","services^category_id",":k:cases_k:services^category_id:2"] },

{ arg:["","_title","%5"] }

	]}
]};

te["case_nb"] = { div:[], c:[ { u:["nb","cases_nb"] }, { div:["e"] } ] };

te["case_title"] = { div:[], c:[ { arg:["","_c","%1"] } ] }; 

te["case_list"] = { list:["case_title","case_nb","bl br ox","case_k","case_r","cases","case_footer"] };

te["case_main"] = { c:
[
	{ div:["tt","vb"], c:
	[
		{ div:["c t03"], c:
		[
			{ div:["","va"], s:["",""], c:
			[
				{ input:["g","","cases_t_","0","radio","1"] },
				{ ac:["c","case_main-cases-vftab","_u","x y cb b h2","::case_title:5:1"] }, 
				{ ac:["c t02 x ay","","_dd","h02 w02 gws_ awb",""] },
				{ div:["e"], arg:["","_title","%5"] }
			]},
			{ div:["dd x y gw ba sh nd w14","vdd"], c:
			[
				{ div:["","va"], ac:["ay","case_main-cases-vftab","_u","xx y cb  n","My Cases"], c:[ { arg:["","_title","my_cases"] } ] },

				{ div:["","va"], ac:["ay","case_main-cases-vftab","_u","xx y cb  n counsellor_","Escalated By Me"], c:[ { arg:["","_title","esca_by_me"] } ] },
				{ div:["","va"], ac:["ay","case_main-cases-vftab","_u","xx y cb  n supervisor_","Escalated By Me"], c:[ { arg:["","_title","esca_by_me"] } ] },
				{ div:["","va"], ac:["ay","case_main-cases-vftab","_u","xx y cb  n casemanager_","Escalated By Me"], c:[ { arg:["","_title","esca_by_me"] } ] },
				
				{ div:["","va"], ac:["ay","case_main-cases-vftab","_u","xx y cb  n supervisor_","Escalated To Me"], c:[ { arg:["","_title","esca_to_me"] } ] },				
				{ div:["","va"], ac:["ay","case_main-cases-vftab","_u","xx y cb  n casemanager_","Escalated To Me"], c:[ { arg:["","_title","esca_to_me"] } ] },												
				{ div:["","va"], ac:["ay","case_main-cases-vftab","_u","xx y cb  n caseworker_","Escalated To Me"], c:[ { arg:["","_title","esca_to_me"] } ] },	

				// { div:["","va"], ac:["ay","case_main-cases-vftab","_u","xx y cb  n","Unread Cases"], c:[ { arg:["","_title","unread_cases"] } ] },
				{ div:["","va"], ac:["ay","case_main-cases-vftab","_u","xx y cb  n","All Cases"], c:[ { arg:["","_title","all_cases"] } ] },
				// { div:["","va"], ac:["ay","case_main-cases-vftab","_u","xx y cb  n","All Cases Today"], c:[ { arg:["","_title","all_cases_today"] } ] },
			]}
		]},

		{ div:["c l40"], c: 
		[
			{ arg:["case_list-cases","","0"] },
			{ input:["g","","cases_t_","0","radio","1"] },
			{ li:["opto x bl bt bb gw s cb","case_list-cases"], ev:["_tab"], c:
			[
				{ s:["c l t h3_ micon","list"] },
				{ div:["c xx y","","List"] }, 
				{ div:["e"] }
			]}
		]},

		{ div:["c"], c: 
		[
			{ arg:["case_rpt_vw-cases-@","","1,0"] },
			{ input:["g","","cases_t_","1","radio"] },
			{ li:["opto x ba gw s cb","case_rpt_main-r_"], ev:["_tab"], c:[ { div:[], c:
			[
				{ s:["c l t h3_ micon","bar_chart"] },
				{ s:["c xx y","Reports"] }, 
				{ div:["e"] }
			]} ]}
		]},

		{ div:["c l40"], ac:["ay","case_f-cases_f","_vpf","x t01 bd_ cb s",""], c:
		[ 
			{ s:["c t04 h3_ micon","search"] },
			{ div:["c x y","","Search"] }, 
			{ div:["e"] }
		]},

		{ div:["c l40"], ac:["ay","cases","_download","x t01 bd_ cb s",""], c:
		[ 
			{ s:["c t04 h3_ micon","download"] },
			{ div:["c x y","","Download"] }, 
			{ div:["e"], arg:["","join","services,referals,clients,perpetrators"] }
		]},

		
		{ div:["e"], c:[ { arg:["","","case_list-cases"] }, { arg:["","","0"] }, { arg:["","","100"] }, { arg:["","",""] } ] }
	]},
	{ div:["yy","vf"], c:[ { div:["","case_f-cases_f"], c: // ev:["_n_vpf"], c:
	[
		{ case_f_tags_k:[] }
	]} ]},
	{ div:[], c:
	[
		{ div:[], c:[ { input:["g","","cases_v","100","radio","1"] }, { p:["tabv yy","vt"], case_list:[] } ] },
		{ div:[], c:[ { input:["g","","cases_v","0","radio"] }, { p:["tabv","vt"] } ] },				
	]}
]};
	
te["cases"] = { c:
[
	{ div:["g"], c:
	[
		{ div:[] },
		{ div:[] },
		{ div:[] },
		{ div:[] },
		{ div:[] },
		{ div:[] },
		{ div:[] },
		{ div:[] }, // blank src // activity_case_ufn needs childNodes.length==0 
	]},
	{ form:[], c:
	[
		{ div:[], c:
		[	
			{ input:["g","","case_vw_vt","0","radio","1"] }, // select reporter
			{ p:["tabv x20 y20 gw mm","vftab"], case_main:[] } 
		]},
		{ div:[], c:
		[	
			{ input:["g","","case_vw_vt","1","radio"] }, // case-edit
			{ p:["tabv gw yy mm","vfvw"] }
		]}
	]}
]};

// -----

function case_postj (el, p_, o) 
{
	console.log ("VooV "+p_.id+","+p_.className);
	var u = el.id.split ("-");
	var p = __(el,"ve");
	var o = {};
	jso (p_.firstChild, o); 	// channel data
	jso (p,o); 			// case details (including reporter|followup)
	url (p, u[0], u[1], o[".id"], null, 2, o, "POST");
}

function _case_postj (ev) { case_postj (this, __(this,"vfvwm"));  boo(ev); }

function _case_postj_update (ev) { case_postj (this, __(elvp,"vfvwm")); boo(ev);  }

