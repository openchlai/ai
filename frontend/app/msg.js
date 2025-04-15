
rk["pmessage_metrics"] = ["pmessage_count","pmessage_percent"];
re["pmessage_metrics"] = 
{
"pmessage_count":	["pmessage_count",	"Count","0","pmessage_rpt_count","pmessage_rpt-pmessages-@:1:0:0"],
"pmessage_percent":	["pmessage_percent",	"Percent","1","pmessage_rpt_percent","pmessage_rpt-pmessages-@:1:1:1"],

}; 

re["pmessage_k"] = 
{
	"vector":["vector","Direction"],
	"user_name":["user_name","Extension"],
	"src":["src","Channel"],

	/*
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
	"justice":["justice","Status in Justice System"],
*/

	"dispositions^disposition":["dispositions^disposition","Disposition"],
	"dispositions^reporter_age_group":["dispositions^reporter_age_group","Reporter Age Group"],
	"dispositions^reporter_sex":["dispositions^reporter_sex","Reporter Sex"],
	"dispositions^reporter_national_id_type":["dispositions^reporter_national_id_type","Reporter ID Type"],
	"dispositions^reporter_nationality":["dispositions^reporter_nationality","Reporter Nationality"],
	"dispositions^reporter_lang":["dispositions^reporter_lang","Reporter Language"],
	"dispositions^reporter_tribe":["dispositions^reporter_tribe","Reporter Tribe"],
	"dispositions^reporter_location_0":["dispositions^reporter_location_0","Reporter Region"], 
	"dispositions^reporter_location_1":["dispositions^reporter_location_1","Reporter District"],
	"dispositions^reporter_location_2":["dispositions^reporter_location_2","Reporter County"],
	"dispositions^reporter_location_3":["dispositions^reporter_location_3","Reporter Sub County"],
	"dispositions^reporter_location_4":["dispositions^reporter_location_4","Reporter Parish"],
	"dispositions^reporter_location_5":["dispositions^reporter_location_5","Reporter Village"],
	"dispositions^reporter_location_6":["dispositions^reporter_location_6","Reporter Constituency"],
};

rk["pmessage_reporters_k"] = [
"dispositions^reporter_age_group", 		"dispositions^reporter_sex", 
"dispositions^reporter_national_id_type", 	"dispositions^reporter_nationality", 
"dispositions^reporter_lang", 			"dispositions^reporter_tribe", 
"dispositions^reporter_location_0", 		"dispositions^reporter_location_1", 
"dispositions^reporter_location_2", 		"dispositions^reporter_location_3", 
"dispositions^reporter_location_4", 		"dispositions^reporter_location_5",
"dispositions^reporter_location_6"];
re["pmessage_reporters_k"] = re["pmessage_k"];

rk["pmessage_cases_k"] = []; //[ "cat_0", "cat_1", "cat_2", "cat_3", "cat_4", "gbv_related", "src", "priority", "status", "created_by", "escalated_to", "escalated_by", "assessment", "justice"];
re["pmessage_cases_k"] = re["pmessage_k"];

rk["pmessage_pmessages_k"] = ["src","vector","user_name","dispositions^disposition"];
re["pmessage_pmessages_k"] = re["pmessage_k"];

// ---

te["pmessage_rpt_metric_tab"] = { div:["c x","%4"], c:
[
	{ arg:["","","0"] },
	{ input:["g","","pmessage_metric","%2","radio","%9"] },
	{ li:["opth x y tc cb","%3","%1"], ev:["_tab"] }
]};

te["pmessage_k_tag"] = { "rpt_axis_tag":["::pmessage_k:0:1","xaxis"] };

te["pmessage_k_r"] = { "rpt_axis_r":["xaxis","pmessage_k_tag","::pmessage_k:0:1"] };

te["pmessage_rpt_ymenu"] = { c:
[
	{ div:["xx t bb_","vb"], c:
	[
		{ div:["c x"], c:[ { input:["g","","pmessage_rpt_vw_t","0","radio","1"] }, { ac:["ay tabu","","_tab","xx y cb","Messages"] } ] },
		//{ div:["c x"], c:[ { input:["g","","pmessage_rpt_vw_t","1","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Case"] } ] },
		{ div:["c x"], c:[ { input:["g","","pmessage_rpt_vw_t","2","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Reporter"] } ] },
		{ div:["e"] }
	]},
	{ div:["xx yy"], c:
	[
		{ div:[], c:[ { input:["g","","pmessage_rpt_vw_tv","0","radio","1"] }, { div:["tabv"], uchk:["pmessage_k_r",null,"pmessage_pmessages_k"] } ] },
		{ div:[], c:[ { input:["g","","pmessage_rpt_vw_tv","1","radio"] }, { div:["tabv"], uchk:["pmessage_k_r",null,"pmessage_cases_k"] } ] },
		{ div:[], c:[ { input:["g","","pmessage_rpt_vw_tv","2","radio"] }, { div:["tabv"], uchk:["pmessage_k_r",null,"pmessage_reporters_k"] } ] },
		//{ div:[], c:[ { input:["g","","pmessage_rpt_vw_tv","3","radio"] }, { div:["tabv"], uchk:["pmessage_k_r",null,"pmessage_clients_k"] } ] },
		//{ div:[], c:[ { input:["g","","pmessage_rpt_vw_tv","3","radio"] }, { div:["tabv"], uchk:["pmessage_k_r",null,"pmessage_perps_k"] } ] },
		//{ div:[], c:[ { input:["g","","pmessage_rpt_vw_tv","4","radio"] }, { div:["tabv"], uchk:["pmessage_k_r",null,"pmessage_services_k"] } ] },
		//{ div:[], c:[ { input:["g","","pmessage_rpt_vw_tv","5","radio"] }, { div:["tabv"], uchk:["pmessage_k_r",null,"pmessage_referals_k"] } ] }
	]}
]};

te["pmessage_rpt_options"] = {  c:
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

te["pmessage_rpt_"] = { c:
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
			{ div:["dd w18 mln7 mt y ba gw sh","vdd"], ev:["_undd"], pmessage_rpt_options:[] }
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
				{ div:["dd y mln47 w50 gw ba mt1","vdd_rpt"], ev:["_undd"], c:[ { pmessage_rpt_ymenu:[null,null,null] } ] }
			]},
			{ div:["d"], uchk:["pmessage_k_tag",null] },
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
	{ div:["","pmessage_rpt_vw-pmessages"], urpt:[] } 
]};

te["pmessage_rpt"] = { pmessage_rpt_:["::pmessage_metrics:4:1","%2","%2","%3","%4","%7"] };  
te["pmessage_rpt_percent"] = { pmessage_rpt_:["Percent", "src","src","src", "src", "-", "pmessage_percent","pmessage_percent"] };
te["pmessage_rpt_count"] = { pmessage_rpt_:["Count", "src","src","src", "src", "-", "pmessage_count","pmessage_count"] };

te["pmessage_rpt_main"] = { c:
[
	{ div:["g xx t15 bb_ s","vb"], c:
	[
		{ s:["c x y cd","Metric:"] },
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
		{ div:[], c:[ { input:["g","","pmessage_rptv","0","radio","1"] }, { p:["tabv","vt"], pmessage_rpt_count:[] } ]},
		{ div:[], c:[ { input:["g","","pmessage_rptv","0","radio"] }, { p:["tabv oh","vt"] } ] },
		{ div:[], c:[ { input:["g","","pmessage_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","pmessage_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","pmessage_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","pmessage_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","pmessage_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","pmessage_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
	]}
]};

// ---------------------------------------------------------------------------------------------

te["pmessage_vw_id"] = { div:["section-to-print tt","ve"], c: 
[	
	{ div:["x20 y","vb"], c:
	[		
		{ div:["c x t02"], ac:["ay","","_uvw","h2 x y bd16 gb cw micon","arrow_back"] },	
		{ s:["c x08 tt h2 b",":v:pmessages:src::case_src:1"] },
		{ s:["c tt h2 b w40",":v:pmessages:src_address"] },
	 	{ div:["d xx y"], c:
		[
			{ input:["g","","sbli_","1","radio","1"] },
			{ input:["g","","sbri__","1","radio"] },
			{ ac:["ao","","_activity_vw","xx bd gg cw",""], c:
			[
				{ s:["c y","Menu"]},
				// { s:["d t03 h2 micon","directions_walk"] },
				{ div:["e"], c:
				[ 
					{ arg:["",".id","-1"] }, 
					{ arg:["","src",":v:pmessages:src"] }, 
					{ arg:["","src_address",":v:pmessages:src_address"] },
					{ arg:["","src_callid",":v:pmessages:src_callid"] }, 
				]}
			]},
		]},	
		{ div:["e"] }
	]},

	{ div:["x25 tt"], c:[ { p:["c w100","nb"], c:[  ] } ] },
		
	{ div:["x30 y20"], c:
	[
		{ u:["activity_message_r","messages","","","desc"] }
	]}	
]};

//------------------------------------------------------------------------------------------------------------------------------------------

te["pmessage_f_tags_"] = { c: 
[
	{ f:["Date",null,		" :d:dmy:0: ","src_ts"," "] },
	{ f:["Direction",null,		" ::vector:0:1","src_vector"," "] },
	{ f:["Phone",null,		" %0","src_address"," "] },
	{ f:["Extension",null,		" %1","user_id"," %1"] },
	{ f:["Source",null,		" %0","src",""] },
	{ f:["Disposition",null,	" %1","dispositions^disposition_id"," %1"] },

	{ f:["Case ID",null,		" %0","dispositions^case_id"," "] },
	
	{ f:["Reporter Name",null,	" %0","dispositions^reporter_fullname",""] },
	{ f:["Reporter Phone",null,	" %0","dispositions^reporter_phone",""] },
	{ f:["Reporter Age",null,	" %1","dispositions^reporter_age_group_id"," %1"] },
	{ f:["Reporter Gender",null,	" %1","dispositions^reporter_sex_id"," %1"] },
	{ f:["Reporter Location",null,	" %1","dispositions^reporter_location_id"," %1"] },
	{ f:["Reporter ID Type",null,	" %1","dispositions^reporter_national_id_type_id"," %1"] },
	{ f:["Reporter Nationality",null," %1","dispositions^reporter_nationality_id"," %1"] },
	{ f:["Reporter Language",null,	" %1","dispositions^reporter_lang_id"," %1"] },
	{ f:["Reporter Tribe",null,	" %1","dispositions^reporter_tribe_id"," %1"] },	

	//{ p:["g","o"], arg:["","_title",null] }, 
	{ div:["e"] }
]};


te["pmessage_f_tags"] = { pmessage_f_tags_:[":k:pmessages_f:src_ts", ":k:pmessages_f:src_vector", ":k:pmessages_f:src_address", ":k:pmessages_f:user_id", 
":k:pmessages_f:src",
":k:pmessages_f:dispositions^disposition_id", 

":k:pmessages_f:dispositions^case_id",

":k:pmessages_f:dispositions^reporter_fullname", 		":k:pmessages_f:dispositions^reporter_phone", 
":k:pmessages_f:dispositions^reporter_age_group_id", 		":k:pmessages_f:dispositions^reporter_sex_id", 
":k:pmessages_f:dispositions^reporter_location_id",
":k:pmessages_f:dispositions^reporter_national_id_type_id", 	":k:pmessages_f:dispositions^reporter_nationality_id", 
":k:pmessages_f:dispositions^reporter_lang_id",			":k:pmessages_f:dispositions^reporter_tribe_id"] };


te["pmessage_f_tags_k"] = { pmessage_f_tags_:[":k:pmessages_k:src_ts:2", ":k:pmessages_k:src_vector:2", ":k:pmessages_k:src_address:2", ":k:pmessages_k:user_id:2", 
":k:pmessages_k:src:2", 
":k:pmessages_k:dispositions^disposition_id:2", 

":k:pmessages_k:dispositions^case_id:2", 

":k:pmessages_k:dispositions^reporter_fullname:2", 		":k:pmessages_k:dispositions^reporter_phone:2", 
":k:pmessages_k:dispositions^reporter_age_group_id:2", 		":k:pmessages_k:dispositions^reporter_sex_id:2", 
":k:pmessages_k:dispositions^reporter_location_id:2",
":k:pmessages_k:dispositions^reporter_national_id_type_id:2", 	":k:pmessages_k:dispositions^reporter_nationality_id:2", 
":k:pmessages_k:dispositions^reporter_lang_id:2", 		":k:pmessages_k:dispositions^reporter_tribe_id:2"] };


te["pmessage_reporters_f"] = { c:
[
	{ div:["xx yy"], kf_s:["Name","dispositions^reporter_fullname",":k:pmessages_f:dispositions^reporter_fullname"] },

	{ div:["xx yy"], kf_s:["Phone","dispositions^reporter_phone",":k:pmessages_f:dispositions^reporter_phone"] },

	{ div:["xx yy"], kf_l:["Age","tag_-r_--o--%1-category_id-dispositions^reporter_age_group_id-%0-%1", "case_lc_main-subcategories", 
":k:pmessages_f:dispositions^reporter_age_group_id", ""," %1","category_id","dispositions^reporter_age_group_id"," %0"," %1", "case_age_group_root_id"] },

	{ div:["xx yy"], kf_l:["Sex","tag_-r_--o--%1-category_id-dispositions^reporter_sex_id-%0-%1", "case_lc_main-subcategories",  
":k:pmessages_f:dispositions^reporter_sex_id", ""," %1","category_id","dispositions^reporter_sex_id"," %0"," %1", "case_sex_root_id"] },

	{ div:["xx yy"], kf_l:["Location","tag_-r_--o--%1-category_id-dispositions^reporter_location_id-%0-%1", "case_location_lc_main-subcategories",  ":k:pmessages_f:dispositions^reporter_location_id", ""," %1","category_id","dispositions^reporter_location_id"," %0"," %1", "case_location_root_id"] },

	{ div:["xx yy"], kf_l:["ID Type","tag_-r_--o--%1-category_id-dispositions^reporter_national_id_type_id-%0-%1", "case_lc_main-subcategories",  ":k:pmessages_f:dispositions^reporter_national_id_type_id", ""," %1","category_id","dispositions^reporter_national_id_type_id"," %0"," %1", "case_national_id_type_root_id"] },

	{ div:["xx yy"], kf_l:["Nationality","tag_-r_--o--%1-category_id-dispositions^reporter_nationality_id-%0-%1", "case_lc_main-subcategories",  ":k:pmessages_f:dispositions^reporter_nationality_id", ""," %1","category_id","dispositions^reporter_nationality_id"," %0"," %1", "case_nationality_root_id"] },

	{ div:["xx yy"], kf_l:["Language","tag_-r_--o--%1-category_id-dispositions^reporter_lang_id-%0-%1", "case_lc_main-subcategories",  ":k:pmessages_f:dispositions^reporter_lang_id", ""," %1","category_id","dispositions^reporter_lang_id"," %0"," %1", "case_lang_root_id"] },

	{ div:["xx yy"], kf_l:["Tribe","tag_-r_--o--%1-category_id-dispositions^reporter_tribe_id-%0-%1", "case_lc_main-subcategories",  ":k:pmessages_f:dispositions^reporter_tribe_id", ""," %1","category_id","dispositions^reporter_tribe_id"," %0"," %1", "case_tribe_root_id"] },

]};

te["pmessage_cases_f"] = { c:
[
	{ div:["xx yy"], kf_s:["CaseID","dispositions^case_id",":k:pmessages_f:dispositions^case_id"] },						
			
	/* 
	{ div:["xx yy"], kf_d:["Created On"," :d:dmy:0: ","created_on",":k:pmessages_f:created_on","created_on",":k:pmessages_f:created_on"] },
			
	{ div:["xx yy"], kf_l:["Created By","tag_-r_--o--%5-user_id-created_by_id-%0-%5",   "user_lc_main-users",":k:pmessages_f:created_by_id", 
""," %1","user_id","created_by_id"," %0"," %1",  "noop"] },

	{ div:["xx yy"], kf_c:["Source","tag_-r_--o--::case_src:0:1--src-%0-",  	":k:pmessages_f:src",
""," %0","","src"," %0","", 				":k:pmessages_f:src","case_src", "src"," %0",""] },
		
	{ div:["xx yy"], kf_l:["Category","tag_-r_--o--%1-category_id-case_category_id-%0-%1",   "case_category_lc_main-subcategories",  ":k:pmessages_f:case_category_id",  ""," %1","category_id","case_category_id"," %0"," %1", "case_category_root_id"] },
	
	{ div:["xx yy"], kf_c:["GBV Related", "tag_-r_--o--::yesno:0:2--gbv_related-%0-",  ":k:pmessages_f:gbv_related",
""," ::yesno:0:2","","gbv_related"," %0","",       ":k:pmessages_f:gbv_related","yesno",  "gbv_related"," ::yesno:0:2",""] },

	{ div:["xx yy"], kf_c:["Priority", "tag_-r_--o--::case_priority:0:1--priority-%0-",  ":k:pmessages_f:priority", 
""," ::case_priority:0:1","","priority"," %0","", 	":k:pmessages_f:priority","case_priority",  "priority"," ::case_priority:0:1",""] },
				
	{ div:["xx yy"], kf_c:["Status", "tag_-r_--o--::case_status:0:1--status-%0-",  	":k:pmessages_f:status",
""," ::case_status:0:1","","status"," %0","", 	":k:pmessages_f:status","case_status",  "status"," ::case_status:0:1",""] },
		
	{ div:["xx yy"], kf_l:["Escalated To","tag_-r_--o--%5-user_id-escalated_to_id-%0-%5",   "user_lc_main-users", ":k:pmessages_f:escalated_to_id", 
""," %1","user_id","escalated_to_id"," %0"," %1", "noop"] },	
		
	{ div:["xx yy"], kf_l:["Case Assessment","tag_-r_--o--%1-category_id-assessment_id-%0-%1",   "case_lc_main-subcategories", ":k:pmessages_f:assessment_id", 
""," %1","category_id","assessment_id"," %0"," %1", "case_assessment_root_id"] },	

	{ div:["xx yy"], kf_l:["Status in Justice System","tag_-r_--o--%1-category_id-justice_id-%0-%1",   "case_lc_main-subcategories", ":k:pmessages_f:justice_id", 
""," %1","category_id","justice_id"," %0"," %1", "case_justice_root_id"] },	
	*/	
				
]};

te["pmessage_pmessages_f"] = { c:
[
	{ div:["xx yy"], kf_d:["Date"," :d:dmy:0: ","src_ts",":k:pmessages_f:src_ts","src_ts",":k:pmessages_f:src_ts"] },

	{ div:["xx yy"], kf_c:["Direction","tag_-r_--o--::vector:0:1--src_vector-%0-",  ":k:pmessages_f:src_vector",
""," ::vector:0:1","","src_vector"," %0","", 	":k:pmessages_f:src_vector","vector", "src_vector"," ::vector:0:1"," "] },	

	{ div:["xx yy"], kf_s:["Phone","src_address",":k:pmessages_f:src_address"] },

	{ div:["xx yy"], kf_l:["Extension","tag_-r_--o--%5-user_id-user_id-%0-%5",   "user_lc_main-users", ":k:pmessages_f:user_id", 
""," %1","user_id","user_id"," %0"," %1", "noop"] },

	{ div:["xx yy"], kf_c:["Source","tag_-r_--o--::case_src:0:1--src-%0-",  	":k:pmessages_f:src",
""," %0","","src"," %0","", 				":k:pmessages_f:src","case_src", "src"," %0",""] },
		
	// { div:["xx yy"], kf_s:["CaseID","dispositions^case_id",":k:pmessages_f:dispositions^case_id"] },			

	{ div:["xx yy"], kf_l:["Disposition","tag_-r_--o--%1-category_id-dispositions^disposition_id-%0-%1", "case_lc_main-subcategories", 
":k:pmessages_f:dispositions^disposition_id", ""," %1","category_id","dispositions^disposition_id"," %0"," %1", "case_disposition_root_id"] },

]};

te["pmessage_f"] = { div:["w55 ma sh__ y gw_","vddvf"], ev:["_undd"], c:
[
	{ s:["x20 t15 n b","Search Messages"] },
	{ div:[], c:
	[
		{ div:["xx t15 bb_","vb"], c:
		[
			{ div:["c x"], c:[ { input:["g","","case_f_vw_t","0","radio","1"] }, { ac:["ay tabu","","_tab","xx y cb","Message"] } ] },
			{ div:["c x"], c:[ { input:["g","","case_f_vw_t","1","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Case"] } ] },
			{ div:["c x"], c:[ { input:["g","","case_f_vw_t","2","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Reporter"] } ] },
			// { div:["c x"], c:[ { input:["g","","case_f_vw_t","3","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Client"] } ] },
			// { div:["c x"], c:[ { input:["g","","case_f_vw_t","4","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Perpetrator"] } ] },
			// { div:["c x"], c:[ { input:["g","","case_f_vw_t","5","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Sevices"] } ] },
			// { div:["c x"], c:[ { input:["g","","case_f_vw_t","6","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Referals"] } ] },
			{ div:["e"] }
		]},
		{ div:["x15 tt b20"], c:
		[
			{ div:[], c:[ { input:["g","","case_f_vw_tv","0","radio","1"] }, { div:["tabv"], pmessage_pmessages_f:[] } ] },
			{ div:[], c:[ { input:["g","","case_f_vw_tv","0","radio"] }, { div:["tabv"], pmessage_cases_f:[] } ] },
			{ div:[], c:[ { input:["g","","case_f_vw_tv","1","radio"] }, { div:["tabv"], pmessage_reporters_f:[] } ] },
			// { div:[], c:[ { input:["g","","case_f_vw_tv","2","radio"] }, { div:["tabv"], pmessage_clients_f:[] } ] },
			// { div:[], c:[ { input:["g","","case_f_vw_tv","3","radio"] }, { div:["tabv"], pmessage_perpetrators_f:[] } ] },
			// { div:[], c:[ { input:["g","","case_f_vw_tv","4","radio"] }, { div:["tabv"], pmessage_services_f:[] } ] },
			// { div:[], c:[ { input:["g","","case_f_vw_tv","5","radio"] }, { div:["tabv"], pmessage_referals_f:[] } ] }
		]}
	]},
	{ p:["g","o"], arg:["","_title",":k:pmessages_f:_title"] },
	{ vp_apply:["pmessage_f_tags-pmessages_f"] }
]};

// ------------------------------------------------------------------------------------------------------------------------------------------

te["pmessage_footer"] = { div:["x ba"], c:
[
	{ div:["d y07"], pg:["pgto","pmessage_list-pmessages"," dh","da dl","pmessage_list-pmessages"," dh","da dr"] },
	{ div:["e"] }
]};

te["pmessage_r_"] = { c:
[
	{ input:["g","","pmessagevwr","1","radio",""] },
	{ ac:["ay w300","pmessage_vw_id-pmessages-@","_vw","cb gw",""], c:
	[
		{ div:["c w17"], s:["xx y08",":d:dmyhnr:6: "] },
		{ div:["c w13"], s:["xx tt b05 h01_",":v:pmessages:src_vector::vector:1"] },
		{ div:["c w15"], s:["xx tt b05 h01_",":v:pmessages:src_address"] },
		{ div:["c w15"], s:["tt b05 h01_  xx",""], c:
		[
			{ s:["c",":v:pmessages:src_usr"] },
			//{ s:["c x",":v:pmessages:user_name"] },
			{ div:["e"] } 
		]},
		{ div:["c w15"], s:["xx tt b05 h01_",":v:pmessages:src"] },
		{ div:["c w15"], s:["xx tt b05 h01_",":v:pmessages:in_count"] },
		{ div:["c w15"], s:["xx tt b05 h01_",":v:pmessages:out_count"] },
		
		{ div:["c w50"], s:["xx y",":v:pmessages:dispositions"] },
		
		{ div:["c w50"], s:["xx y",":v:pmessages:contacts"] },
	
		{ div:["e"], c:[ { arg:["",".id","%0"] } ] }
	]}
]};

te["pmessage_r"] = { li:["w300","va"], pmessage_r_:[] };

te["pmessage_k"] = { div:["w300 bt bb"], s:["",""], c: // activate filter ctx
[
	{ k_a:["c w17","messages_rr-messages","cd","Date","da db",	"src_ts",	":k:pmessages_k:src_ts:2"] },
	{ k_a:["c w13","messages_rr-messages","cd","Direction","da db",	"src_vector",	":k:pmessages_k:src_vector:2"] },
	{ k_a:["c w15","messages_rr-messages","cd","Phone","da db",	"src_address",	":k:pmessages_k:src_address:2"] },
	{ k_a:["c w15","messages_rr-messages","cd","Extension","da db",	"src_usr",	":k:pmessages_k:src_usr:2"] },
	{ k_a:["c w15","messages_rr-messages","cd","Source","da db",	"src",		":k:pmessages_k:src:2"] },
	{ k_a:["c w15","messages_rr-messages","cd","Messages","da db",	"in_count",	":k:pmessages_k:in_count:2"] },
	{ k_a:["c w15","messages_rr-messages","cd","Replies","da db",	"out_count",	":k:pmessages_k:out_count:2"] },
//	{ k_a:["c w15","messages_rr-messages","w12 cd ","QA Score","da db","qa_done",	":k:messages_k:qa_done:2"] },
	{ k_a:["c w50","messages_rr-messages","w12 cd ","Disposition","da db","dispositions^disposition_id",":k:pmessages_k:dispositions^disposition_id:2"] },
	{ k_a:["c w50","messages_rr-messages","w12 cd ","Reporter","da db","dispositions^reporter_id",":k:pmessages_k:dispositions^reporter_id:2"] },	
	
	{ div:["e"], c:
	[
		{ arg:["","dispositions^case_id",		":k:pmessages_k:dispositions^case_id:2"] },
		{ arg:["","dispositions^reporter_contact_id",	":k:pmessages_k:dispositions^reporter_contact_id:2"] },
		{ arg:["","dispositions^reporter_fullname",	":k:pmessages_k:dispositions^reporter_fullname:2"] },
		{ arg:["","dispositions^reporter_phone",	":k:pmessages_k:dispositions^reporter_phone:2"] },
		{ arg:["","dispositions^reporter_age_group_id",	":k:pmessages_k:dispositions^reporter_age_group_id:2"] },
		{ arg:["","dispositions^reporter_sex_id",	":k:pmessages_k:dispositions^reporter_sex_id:2"] },
		{ arg:["","dispositions^reporter_location_id",	":k:pmessages_k:dispositions^reporter_location_id:2"] },
		{ arg:["","dispositions^reporter_national_id_type_id",":k:pmessages_k:dispositions^reporter_national_id_type_id:2"] },
		{ arg:["","dispositions^reporter_nationality_id",":k:pmessages_k:dispositions^reporter_nationality_id:2"] },
		{ arg:["","dispositions^reporter_lang_id",	":k:pmessages_k:dispositions^reporter_lang_id:2"] },
		{ arg:["","dispositions^reporter_tribe_id",	":k:pmessages_k:dispositions^reporter_tribe_id:2"] },
	]}
]};

te["pmessage_nb"] = { div:[], c:[ { u:["nb","pmessages_nb"] }, { div:["e"] } ] };

te["pmessage_title"] = { div:[] }; 

te["pmessage_list"] = { list:["pmessage_title","pmessage_nb","bl br ox","pmessage_k","pmessage_r","pmessages","pmessage_footer"] };

te["pmessage_main"] = { c:
[
	{ div:["tt","vb"], c:
	[
		{ div:["c t03"], c:
		[
			{ div:["","va"], s:["",""], c:
			[
				{ input:["g","","pmessage_t_","0","radio","1"] },
				{ ac:["c","pmessage_main-pmessages-vftab","_u","x y cb b h2","Other Channels"] }, 
				//{ ac:["c t02 x ay","","_dd","h02 w02 gws_ awb",""] },
				{ div:["e"] } //, arg:["","_title","%5"] }
			]},
			{ div:["dd x y gw ba sh nd w14","vdd"], c:
			[
			
			]}
		]},
		
		{ div:["c l40"], c: 
		[
			{ arg:["pmessage_list-pmessages","","0"] },
			{ input:["g","","pmessages_t_","0","radio","1"] },
			{ li:["opto x bl bt bb gw s cb","pmessage_list-pmessages"], ev:["_tab"], c:
			[
				{ s:["c l t h3_ micon","list"] },
				{ div:["c xx y","","List"] }, 
				{ div:["e"] }
			]}
		]},

		{ div:["c"], c: 
		[
			{ arg:["pmessage_rpt_vw-pmessages-@","","1,0"] },
			{ input:["g","","pmessages_t_","1","radio"] },
			{ li:["opto x ba gw s cb","pmessage_rpt_main-r_"], ev:["_tab"], c:[ { div:[], c:
			[
				{ s:["c l t h3_ micon","bar_chart"] },
				{ s:["c xx y","Reports"] }, 
				{ div:["e"] }
			]} ]}
		]},

		{ div:["c l40"], ac:["ay","pmessage_f-pmessages_f","_vpf","x t01 bd_ cb s",""], c:
		[ 
			{ s:["c t04 h3_ micon","search"] },
			{ div:["c x y","","Search"] }, 
			{ div:["e"] }
		]},

		{ div:["c l40"], ac:["ay","pmessages","_download","x t01 bd_ cb s",""], c:
		[ 
			{ s:["c t04 h3_ micon","download"] },
			{ div:["c x y","","Download"] }, 
			{ div:["e"] }
		]},
		
		{ div:["e"], c:[ { arg:["","","pmessage_list-pmessages"] }, { arg:["","","0"] }, { arg:["","","-1"] }, { arg:["","",""] } ] }
	]},

	{ div:["yy","vf"], c:[ { div:["","pmessage_f-pmessages_f"], c: // ev:["_n_vpf"], c:
	[
		{ pmessage_f_tags_k:[] }
	]} ]},

	{ div:[], c:
	[
		{ div:[], c:[ { input:["g","","pmessages_v","0","radio","1"] }, { p:["tabv yy","vt"], pmessage_list:[] } ] },
		{ div:[], c:[ { input:["g","","pmessages_v","1","radio"] }, { p:["tabv","vt"] } ] },				
	]}
]};
	
te["pmessages"] = { c:
[
	{ div:["g"], c:
	[
		
	]},
	{ form:[], c:
	[
		{ div:[], c:
		[	
			{ input:["g","","pmessage_vw_vt","0","radio","1"] }, 
			{ p:["tabv x20 y20 gw mm","vftab"], pmessage_main:[] } 
		]},
		{ div:[], c:
		[	
			{ input:["g","","pmessage_vw_vt","1","radio"] }, 
			{ p:["tabv gw yy mm","vfvw"] }
		]}
	]}
]};

