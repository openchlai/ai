
// -----------------------------------------------------------------------------------------

te["activity_case_notify_vw_id"] = { c:
[
	{ div:[], c:
	[
		{ input:["g","","activity_vw_vt2","1","radio"] }, // search reporter
		{ p:["tabv ","vftab"], u:["activity_match_main","activities"] } 
	]},
	{ div:[], c:
	[	
		{ input:["g","","activity_vw_vt2","1","radio","1"] }, // case-form (new|followup)
		{ p:["tabv ","vfvw"], u:["case_vw_id","cases"] }
	]}
]};
	
te["activity_case_notify"] = { activity_vw_id_tabs_:["","noop","1","activity_case_notify_vw_id"] };

// -----------------------------------------------------------------------------------------

te["activity_message_sended"] = { ufn:["activity_message_sended"] };

te["activity_messages_ufn"] = { ufn:["activity_messages_ufn"] };

te["activity_messages_txt"] = { div:["ba_b"], c:
[
	{ div:[], c:
	[
		{ div:["d w13 g"], ac:["abs w12 x y ","","","xx y cd tr","Preset Replies"] },
		{ div:["e"] }
	]},
	{ div:[""], c:[ { textarea:["wp100 h09 ll r130 yy","","src_msg","","Reply ..."], ev:["","","_msg"] } ] }
]}

te["activity_message_r_v_o"] = { div:["ba"], c:
[ 
	{ s:["c x y b w15",null] },
	{ s:["c x y bl",null] }, 
	{ div:["e"] } 
]},

te["activity_message_r_v"] = { c:[ { pre:[":v:messages:src_vector::vector:11","",null] }, { div:["e"] } ] },

te["activity_message_r_"] = { c: 
[
	{ arg:["","","%0"] },
	{ div:[":v:messages:src_vector::vector:10"], c:
	[
		{ div:[], umime:["activity_message_r_v", ":v:messages:src_mime", ":v:messages:src_msg", ":v:messages:src::case_src:12"] },
		{ div:[":v:messages:src_vector::vector:12"], c:
		[
			{ div:[":v:messages:src_vector::vector:13"], s:["x bd gr cw m",":v:messages:src_status"] },
			{ s:[":v:messages:src_vector::vector:13", ":r::1:: : ago:: : ago:"] },
 { arg:["tm","","%1"] },
			{ div:[":v:messages:src_vector::vector:13"], s:[":v:messages:src_vector::vector:14",":v:messages:created_by"] },
			//{ arg:["tm","","%1"] },
			{ div:["e"] }
		]},
	]},
	{ div:["e"] }
]};

te["activity_message_r"] = { div:["y"], activity_message_r_:[] };

te["activity_messages"] = { c:
[
	{ div:[] }, // inbound nb // todo: display captured fields status
	{ p:["tt ","msgs"], c:
	[
		{ div:["l30 r40 yy oy scroller"], c:
		[
			{ u:["activity_message_r","messages","","","desc"] },
			{ ufn:["activity_messages_height"] },
		]},
		{ div:[] }
	]},
	{ div:["","ve"], c:
	[
		{ p:["x30 y20","o"], c:
		[
			 { div:[], c:
			 [
 				{ div:["d w08"], c:
 				[
 					{ ac:["abs btn ao t","","_activity_message_send"," t30 tc ba_b bd w08 h05 cb","Send"] },
 					{ div:["abs"], s:["w08 h05 t30 tc h05 go b savl","..."] } 
 				]},
 				{ div:["e"] }
			 ]},
			 { p:["mr10","sended"], activity_messages_txt:[] }
		]}
	]}
]};

te["activity_vw_id_messages_match"] = { activity_vw_id_tabs_:["","activity_messages","1","activity_match_main"] };

te["activity_vw_id_messages"] = { activity_vw_id_tabs_:["1","activity_messages","","activity_match_main"] };

// --------------------------------------------------------------------------------------------------------------------

te["activity_contact_case_nb"] = { div:["w50 x20 y15 ma sh__ gw_ bd","vddvw"], ev:["_undd"], c:
[
        { div:[""], c:
        [
                { s:["c x y12 n b","Error"] },
                { ac:["d","","_uvp","x y h cb","&Cross;"] },
                { div:["e"] }
        ]},
        { div:["","ve"], c:
        [ 
                { div:["t b20"], c:
                [ 
                        { s:["xx y07 gp cr n","Unknown Contact"] },
                        { s:["xx y20 cb ","%0"] },
                ]},

        ]}
]};

// --------------------------------------------------------------------------------------------------------------------

te["activity_disposition_ed_r"] = { div:["",":c:r:0"], c:
[
	{ input:["g","","disposition_id","%0","radio"] },
	{ ac:["rg rc r ay bd_","","_opt","xx t02 cb",""], c:
	[
		{ div:["c w01_ t"], s:["opt",""] },
		{ div:["c x y w35"], uval:["",":v:categories:fullname"] },
		{ div:["e"] }			
	]}
]};

te["activity_disposition_src_address"] = { arg:["",":v:cases:src::case_src:11",":v:cases:src_address"] };

te["activity_disposition_no_contact"] = { div:[""], c:
[
	{ s:["xx tt gy cd n","You did not select a Contact."] },
	{ s:["xx y07 gy cd n","Please indicate the Callers Sex and Location."] },
	{ div:["t15"], c:
	[
		// { div:["c w21"], case_contact_ed_age:["","","","",""," %0"] },
		{ div:["c w21"], case_sex_enum:["Sex","",""," %0"] },
		{ div:["c w41"], case_loc_enum:["Location","",""," %0"] },
		{ p:["e","o"], u:["activity_disposition_src_address","cases"] }
	]}
]};

te["activity_disposition_new"] = { div:["w50 x20 y15 ma sh__ gw_ bd","vddvw"], ev:["_undd"], c:
[
	{ div:[""], c:
	[
		{ s:["c x y12 h3 b","Disposition"] },
		{ ac:["d","","_uvp","x y h cb","&Cross;"] },
		{ div:["e"] }
	]},
	{ div:["","ve"], c:
	[
		{ div:[], c:[ { p:["c","nb"] }, { div:["e"] } ] },
		{ div:["t b20"], c:
		[
			{ activity_disposition_no_contact:[] },
			{ u:["activity_disposition_contact_r","contacts_uuid","","contacts_uuid"] }
		]},
		{ p:["h20 oy ba_ bd dispob","o"], u:["activity_disposition_ed_r","subcategories"] },
		// { p:["",""], c:[ { textarea:[] } ] } // comments
		{ ac:["t30 ao btn","activity_disposition-dispositions","_activity_postj","y07 gb bd cw b n tc","Submit"] },
	]}
]};

// ---

te["activity_disposition_vwr_case"] = { div:["xx y07 mb"], c:
[
	{ div:["x tt"], c:
	[
		{ s:["c x y b",CASE_ID_PREFIX] },
		{ s:["c y b",":v:cases:id"] },
		{ ac:["d ao","case_vw_id-cases_uuid-@","_vw","xx y bd16 cw gb",""], c:
		[
			//{ s:["c x t04 h2 b","+"] },
			{ s:["c","Followup"] },
			{ div:["e"], c:[ { arg:["",".id","-1"] }, { arg:["","case_id",":v:cases:id"] }, { arg:["","reporter_uuid_id",":v:cases:reporter_id"] } ] }
		]}, 
		{ div:["e"] }
	]},
	{ div:["x tt"], c:
	[
		{ s:["x t cd","Case Category"] },
		{ div:["x t"], uval:["",":v:cases:case_category"] },
		{ div:["e"] }
	]},
	{ div:["x tt"], c:
	[
		{ s:["x t cd","Case Narrative"] },
		{ div:["x t"], s:["",":v:cases:narrative"] },
		{ div:["e"] }
	]},
	{ div:["x tt"], c:
	[
		{ s:["x t cd","Case Plan"] },
		{ div:["x t"], s:["",":v:cases:plan"] },
		{ div:["e"] }
	]},
	{ div:["x tt"], c:
	[
		{ s:["c x t cd","Priority"] },
		{ s:["d x t cd","Status"] },
		{ div:["e"] }
	]},
	{ div:["x"], c:
	[
		{ div:["c x t"], s:["",":v:cases:priority::case_priority:2"] },
		{ div:["d x t"], s:["",":v:cases:status::case_status:1"] },
		{ div:["e"] }
	]},
	
	{ div:[], usub:["case_vw_refered_to_none,case_vw_refered_to_dept_sub,case_vw_refered_to_sub","cases",":v:cases:is_refered_to","0,1,2"] },

	{ div:[], usub:["case_vw_escalated_to_sub","cases",":v:cases:is_escalated_to","1"] } 
]};


te["activity_disposition_vwr_contact_"] = { c:
[
        { div:["xx t"], c:
	[
		{ s:["c b r05",":v:contacts:fullname"] },
		{ div:["c xx"], uval:["",":v:contacts:sex"] },
		{ div:["c"], uval:["",":v:contacts:age_group"] },
		{ div:["e"] }
	]},
	{ div:["xx tt "], c:
	[
		{ div:["abs"], c:
		[
			{ s:["micon t02 h3","place"] },
		]},
		{ div:["ml3"], s:["",""], c:
		[
			{ div:["c r10"], uval:["",":v:contacts:location"] },
			{ s:["c t03 cd",":v:contacts:landmark"] },
			{ div:["e"] }
		]},
		{ div:["e"] }
	]},
	{ div:["xx tt"], c:
	[
		{ s:["c w03 micon h3","call"] },
		{ s:["c ",":v:contacts:phone"] },
		{ s:["c xx ",":v:contacts:phone2"] },
		{ div:["e"] }
	]},
	{ div:["xx tt"], c:
	[
		{ s:["c w03 micon h3","email"] },
		{ s:["c",":v:contacts:email"] },
		{ div:["e"] }
	]},
]};

te["activity_disposition_contact_r"] = { div:["bl2_b"], c:
[
	{ activity_disposition_vwr_contact_:[] },
	{ p:["g","o"], arg:["","contact_id","%0"] }
]};

te["activity_disposition_vwr_contact"] = { c:
[
	{ input:["g","","activity_contact_id",":v:contacts:id","radio","1"] },
	{ div:["xx y07 mb"], c: 
	[
		{ div:["x"], c:
		[
			{ div:["d w03"], c:
			[
				{ input:["g","","advwt","%0","radio"] },
				{ ac:["ab abs","","_activity_disposition_uvwr","x y tr cb h3 gws_",""], c:
				[
					{ s:["","&Cross;"] },
				]},
			]},
			{ div:["e"] }
		]},
		{ div:[], c:
		[
			{ activity_disposition_vwr_contact_:[] },
			{ div:["tt"], c:
			[
				{ div:["c"], c:
				[
					{ ac:["ay","case_contact_ed-contacts-^","_vp","xx y04",""], c:
					[
						{ s:["","Edit"] },
						{ div:["g"], arg:["",".id",":v:contacts:id"] }
					]},
					{ div:["g"], arg:["","","activity_disposition_vwr_contact-contacts-va--@"] }, // vp return anchor
				]},
				{ div:["e"] }
			]}
		]},
		{ div:["x g"], c:[ { u:["nb","contacts_nb"] }, { div:["e"] } ] }	
	]}
]};

te["activity_disposition_vwr"] = { c:
[
	{ div:["bl2_b","va"], u:["activity_disposition_vwr_contact","contacts"] },
	{ div:["bl2_b","va"], u:["activity_disposition_vwr_case","cases_related"] } 
]};

// ---

te["activity_disposition_footer"] = { c:
[
	{ div:["x20 y15"], c:
	[
		{ div:["l08"], pg:["pgto","activity_disposition-dispositions"," dh","da dl","activity_disposition-dispositions"," dh","da dr"] },
		{ div:["e"] }
	]}
]};

te["activity_disposition_r_case"] = { c:
[
	{ s:["c l t cb",CASE_ID_PREFIX] },
	{ s:["c x t cb",":v:dispositions:case_id"] },
	{ div:["c l15 y02"], uval:["",":v:dispositions:case_category"] },
	//{ s:["c x20 t cd",":v:dispositions:case_priority::case_priority:2"] },
	//{ s:["c t cd",":v:dispositions:case_status::case_status:1"] },
	{ div:["e"] }
]};

te["activity_disposition_r_contact"] = { c:
[
	{ div:["c t02 r10"], s:["x08 y03 bd8 gws_",":v:dispositions:reporter_fullname"] },
]};

te["activity_disposition_r_"] = { div:["l25"], c:
[
	{ input:["g","","advwt","%0","radio"] },
	{ li:[null], ev:["_activity_disposition_vwr"], c:
	[
		{ div:["abs xx tt"], s:["x y micon h3 ba gws_ bd16",":v:dispositions:src::case_src:6"] },
		{ div:[null], c:
		[
			{ div:[], c:
			[
				{ u:[":u::22:0:noop:activity_disposition_r_contact"] },
				{ div:["c x y b"], uval:["",":v:dispositions:disposition"] },	
				{ div:["e"] }	
			]},
			{ div:[], u:[":u::57:0:noop:activity_disposition_r_case"] },
			{ div:["cd"], c:
			[
				{ s:["c l y",":r::1:: : ago:: : ago:"] },
				{ arg:["tm","","%1"] },
				{ s:["c x20 y",":v:dispositions:created_by"] },
				{ p:["e","o"], arg:["",".id","%0"] }	
			]}
		]}
	]}
]};

te["activity_disposition_r"] = { activity_disposition_r_:["lr l","ml2_ mh05 x30 yy bl r"] };

te["activity_disposition_r_new"] = { c:[ { activity_disposition_r_:["lr l gh","ml2_ mh05 x30 yy bl3_g r"] } /*,{ activity_disposition_ufn:[] }*/ ] };

te["activity_disposition_r_new_contact"] = { u:["activity_disposition_r_new","dispositions"] };

te["activity_disposition_k"] = { div:["g"], c:
[
	{ arg:["","reporter_id",		":k:dispositions_k:reporter_id:2"] },
	{ arg:["","reporter_contact_id",	":k:dispositions_k:reporter_contact_id:2"] },
	{ arg:["","reporter_fullname",		":k:dispositions_k:reporter_fullname:2"] },
	{ arg:["","reporter_phone",		":k:dispositions_k:reporter_phone:2"] },
	{ arg:["","reporter_email",		":k:dispositions_k:reporter_email:2"] },
	{ arg:["","reporter_location_id",	":k:dispositions_k:reporter_location_id:2"] },
	
	{ arg:["","case_id",			":k:dispositions_k:case_id:2"] },
	{ arg:["","cases^created_on",		":k:dispositions_k:cases^created_on:2"] },
	{ arg:["","cases^created_by_id",	":k:dispositions_k:cases^created_by_id:2"] },
	{ arg:["","src",			":k:dispositions_k:src:2"] },
	{ arg:["","cases^case_category_id",	":k:dispositions_k:cases^case_category_id:2"] },
	{ arg:["","cases^priority",		":k:dispositions_k:cases^priority:2"] },
	{ arg:["","cases^status",		":k:dispositions_k:cases^status:2"] },
	{ arg:["","cases^refered_to_dept_id",	":k:dispositions_k:cases^refered_to_dept_id:2"] },
	{ arg:["","cases^refered_to_id",	":k:dispositions_k:cases^refered_to_id:2"] },
	{ arg:["","cases^escalated_to_id",	":k:dispositions_k:cases^escalated_to_id:2"] },
		
	{ arg:["","_c","%1"] },
]};

te["activity_disposition_nb"] = { div:[] };

te["activity_disposition_title"] = { div:[], c:[ { p:["","vdisp"] } ] };

te["activity_disposition"] = { list:["activity_disposition_title", "activity_disposition_nb", "", "activity_disposition_k", "activity_disposition_r", "dispositions", "activity_disposition_footer"] };

// --------------------------------------------------------------------------------------------------------------------

te["activity_match_f_tags_"] = { c: 
[
	{ f:["Reporter Name",null,	" %0","reporter_fullname",""] },
	{ f:["Reporter Age",null,	" %1","reporter_age_group_id"," %1"] },
	{ f:["Reporter Sex",null,	" %1","reporter_sex_id"," %1"] },
	{ f:["Reporter Phone",null,	" %0","reporter_phone",""] },
	{ f:["Reporter Email",null,	" %0","reporter_email",""] },
	{ f:["Reporter Location",null,	" %1","reporter_location_id"," %1"] },

	{ f:["Case ID",null,		" %0","case_id",""] },
	{ f:["Created On",null,		" :d:dmy:0: ","cases^created_on",""] },
	{ f:["Created By",null,		" %1","cases^created_by_id"," %1"] },
	{ f:["Source",null,		" ::case_src:0:1","src",""] },
	{ f:["Category",null,		" %1","cases^case_category_id"," %1"] },
	{ f:["GBV Related",null,        " ::yesno:0:2","cases^gbv_related",""] },
	{ f:["Priority",null,		" ::case_priority:0:1","cases^priority",""] },
	{ f:["Status",null,		" ::case_status:0:1","cases^status",""] },
	{ f:["Escalated To",null,	" %1","cases^escalated_to_id"," %1"] },
	{ f:["Case Assessment",null,	" %1","cases^assessment_id"," %1"] },
	{ f:["Status in Justice System",null," %1","cases^justice_id"," %1"] },
	
	{ p:["g","o"], arg:["","sort","id"] }, 
	{ div:["e"] }
]};

te["activity_match_f_tags_k"] = { activity_match_f_tags_:
[
":k:dispositions_k:reporter_fullname:2",":k:dispositions_k:reporter_age_group_id:2", 	":k:dispositions_k:reporter_sex_id:2", 
":k:dispositions_k:reporter_phone:2", 	":k:dispositions_k:reporter_email:2", 		":k:dispositions_k:reporter_location_id:2",
":k:dispositions_k:case_id:2", 		":k:dispositions_k:cases^created_on:2", 	":k:dispositions_k:cases^created_by_id:2", 
":k:dispositions_k:src:2", 		":k:dispositions_k:cases^case_category_id:2", 	":k:dispositions_k:cases^gbv_related:2",
":k:dispositions_k:cases^priority:2", 	":k:dispositions_k:cases^status:2", 		":k:dispositions_k:cases^escalated_to_id:2", 
":k:dispositions_k:cases^assessment_id:2",":k:dispositions_k:cases^justice_id:2",   
]};

te["activity_match_f_tags"] = { activity_match_f_tags_:
[
":k:dispositions_f:reporter_fullname", 	":k:dispositions_f:reporter_age_group_id", 	":k:dispositions_f:reporter_sex_id",
":k:dispositions_f:reporter_phone", 	":k:dispositions_f:reporter_email", 		":k:dispositions_f:reporter_location_id",
":k:dispositions_f:case_id", 		":k:dispositions_f:cases^created_on", 		":k:dispositions_f:cases^created_by_id", 
":k:dispositions_f:src", 		":k:dispositions_f:cases^case_category_id", 	":k:dispositions_f:cases^gbv_related", 
":k:dispositions_f:cases^priority", 	":k:dispositions_f:cases^status", 		":k:dispositions_f:cases^escalated_to_id",  
":k:dispositions_f:cases^assessment_id",":k:dispositions_f:cases^justice_id",  
]};

te["activity_match_cases_f"] = { c:
[
	{ div:["xx yy"], kf_s:["Case ID","case_id",":k:dispositions_f:case_id"] },			
			
	{ div:["xx yy"], kf_d:["Created On"," :d:dmy:0: ","cases^created_on",":k:dispositions_f:cases^created_on","cases^created_on",":k:dispositions_f:cases^created_on"] },
			
	{ div:["xx yy"], kf_l:["Created By","tag_-r_--o--%5-user_id-cases^created_by_id-%0-%5",   "user_lc_main-users",":k:dispositions_f:cases^created_by_id", 
""," %1","user_id","cases^created_by_id"," %0"," %1",  "noop"] },

	{ div:["xx yy"], kf_c:["Source","tag_-r_--o--::case_src:0:1--src-%0-",  	":k:dispositions_f:src",
""," %0","","src"," %0","", 				":k:dispositions_f:src","case_src", "src"," %0",""] },
		
	{ div:["xx yy"], kf_l:["Category","tag_-r_--o--%1-category_id-cases^case_category_id-%0-%1",   "case_category_lc_main-subcategories",  ":k:dispositions_f:cases^case_category_id",  ""," %1","category_id","cases^case_category_id"," %0"," %1", "case_category_root_id"] },
	
	{ div:["xx yy"], kf_c:["GBV Related", "tag_-r_--o--::yesno:0:2--cases^gbv_related-%0-",  ":k:dispositions_f:cases^gbv_related",
""," ::yesno:0:2","","cases^gbv_related"," %0","",       ":k:dispositions_f:cases^gbv_related","yesno",  "cases^gbv_related"," ::yesno:0:2",""] },

	{ div:["xx yy"], kf_c:["Priority", "tag_-r_--o--::case_priority:0:1--cases^priority-%0-",  ":k:dispositions_f:cases^priority", 
""," ::case_priority:0:1","","cases^priority"," %0","", 	":k:dispositions_f:cases^priority","case_priority",  "cases^priority"," ::case_priority:0:1",""] },
				
	{ div:["xx yy"], kf_c:["Status", "tag_-r_--o--::case_status:0:1--cases^status-%0-",  	":k:dispositions_f:cases^status",
""," ::case_status:0:1","","cases^status"," %0","", 	":k:dispositions_f:cases^status","case_status",  "cases^status"," ::case_status:0:1",""] },
		
	{ div:["xx yy"], kf_l:["Escalated To","tag_-r_--o--%5-user_id-cases^escalated_to_id-%0-%5",   "user_lc_main-users", ":k:dispositions_f:cases^escalated_to_id", 
""," %1","user_id","cases^escalated_to_id"," %0"," %1", "noop"] },

	{ div:["xx yy"], kf_l:["Case Assessment","tag_-r_--o--%1-category_id-cases^assessment_id-%0-%1",   "case_lc_main-subcategories", ":k:dispositions_f:cases^assessment_id", 
"", " %1", "category_id", "cases^assessment_id"," %0"," %1", "case_assessment_root_id"] },	

	{ div:["xx yy"], kf_l:["Status in Justice System","tag_-r_--o--%1-category_id-cases^justice_id-%0-%1",   "case_lc_main-subcategories", ":k:dispositions_f:cases^justice_id", 
""," %1","category_id","cases^justice_id"," %0"," %1", "case_justice_root_id"] },		
					
]};

te["activity_match_contacts_f"] = { c:
[
	{ div:["xx yy"], kf_s:["Reporter Name","reporter_fullname",":k:dispositions_f:reporter_fullname"] },
	
	{ div:["xx yy"], kf_l:["Reporter Age","tag_-r_--o--%1-category_id-reporter_age_group_id-%0-%1", "case_lc_main-subcategories", 
":k:dispositions_f:reporter_age_group_id", ""," %1","category_id","reporter_age_group_id"," %0"," %1", "case_age_group_root_id"] },

	{ div:["xx yy"], kf_l:["Reporter Sex","tag_-r_--o--%1-category_id-reporter_sex_id-%0-%1", "case_lc_main-subcategories",  
":k:dispositions_f:reporter_sex_id", ""," %1","category_id","reporter_sex_id"," %0"," %1", "case_sex_root_id"] },

	{ div:["xx yy"], kf_s:["Reporter Phone","reporter_phone",":k:dispositions_f:reporter_phone"] },
	
	{ div:["xx yy"], kf_s:["Reporter Email","reporter_email",":k:dispositions_f:reporter_email"] },
	
	{ div:["xx yy"], kf_l:["Reporter Location","tag_-r_--o--%1-category_id-reporter_location_id-%0-%1", "case_location_lc_main-subcategories",  ":k:dispositions_f:reporter_location_id", ""," %1","category_id","reporter_location_id"," %0"," %1", "case_location_root_id"] },
]};

te["activity_match_f"] = { div:["w60 ma sh__ y gw_ bd","vddvf"], ev:["_undd"], c:
[
	{ div:["x15"], c:
	[
		{ s:["x t15 h3 b","Search"] },
		{ div:["x t20","vb"], s:["",""], c:
		[
			{ div:["c"], c:[ { input:["g","","case_f_vw_t","0","radio","1"] }, { ac:["ay tabu","","_tab","x03 y cb","Contacts"] } ] },
			{ div:["c l20"], c:[ { input:["g","","case_f_vw_t","1","radio"] }, { ac:["ay tabu","","_tab","x03 y cb","Cases"] } ] },
			{ div:["e"] }
		]},
		{ div:["y15"], c:
		[
			{ div:[], c:[ { input:["g","","case_f_vw_tv","0","radio","1"] }, { div:["tabv"], activity_match_contacts_f:[] } ] },
			{ div:[], c:[ { input:["g","","case_f_vw_tv","1","radio"] }, { div:["tabv"], activity_match_cases_f:[] } ] },		
		]}
	]},
	{ vp_apply:["activity_match_f_tags-dispositions_f"] }
]};

te["activity_match_list_contacts"] = { c:  
[
	{ activity_contact_k:[] }, 
	{ uv:["activity_contact_list","contacts"] } // cascade filter to contacts
]};	
	
te["activity_match_list"] = { c:
[
	{ div:[], c:[ { arg:["","_c","10"] } ] }, // needed for corect filtering // div also needed by uvpf
	
	{ div:[], c:
	[ 
		{ div:["d w55"], s:["w55 abs gws",""] },	
		{ div:["e"] }
	]},
	
	{ div:["mr60","vt"], u:["activity_disposition","dispositions_ctx"] },
]};

te["activity_match_list_none"] = { c:
[
        { div:[], c:[ { arg:["","_c","10"] } ] }, // needed for corect filtering // div also needed by uvpf

        { div:[], c:
        [
                { div:["d w55"], s:["w55 abs gws",""] },
                { div:["e"] }
        ]},

        { div:["mr60","vt"], c:
	[
		{ div:[], c:[ { p:["","vdisp"] } ] }
	]}
]};

te["activity_match_"] = { c: 
[
	{ div:["","vb"], c:
	[
		{ div:[""], c:
		[
			
		]},
		
		{ div:["xx tt"], c:
		[
			{ div:["c"], c:
			[
				{ div:["","va"], s:["",""], c:
				[
					{ input:["g","","cases_t_","0","radio","1"] },
					{ ac:["c r20","activity_match-activities-vftab","___u","xx y08 cb b h3","Activity History"] }, 
					
					{ div:["c g"], ac:["xx bd","","","x y cb",""], c:
					[
						{ s:["c h2 micon mln1_ gws","face"] },
						{ s:["c h2 micon mln1_ gws","face"] },
						{ s:["c h2 micon mln1_ gws","face"] },
						{  s:["c l t02","??? Contacts"] }, 
						{ div:["e"] }
					]},
					
					//{ ac:["c t x ay","","_dd","h02 w02 awb gws_",""] },
					{ div:["e"] }
				]},
				{ div:["dd w15 x yy gw ba sh nd w16","vdd"], c:
				[
					{ s:["x y","matching contacts"] }
					//{ div:["","va"], ac:["ay","sasas","--aa","xx y cb","Activity History"] },
					//{ div:["t","va"], ac:["ay","sasas","aa-as","xx y cb","Matching Contacts"] },
				]}
			]},		
			
			{ div:["c xx"], c:
			[
				{ ac:["ay t03","activity_match_f-dispositions_f","_vpf","xx bd16  cb",""], c:
				[ 
					{ s:["c t04 h3_ micon","search"] },
					{ div:["c x y s","","Search"] }, 
					{ div:["e"] }
				]}
			]},
			
			/*
			{ div:["c xx g"], c:
			[
				{ input:["g","","activity_vw_vt3","1","radio"] },
				{ ac:["ay","case_contact_new-r_-^","_vp","xx bd16 gg cw",""], c:
				[
					{ s:["c x t04 h2 b","+"] },				
					{ s:["c x y s","New Reporter"] },
					{ div:["e"], c:[ { arg:["phone-8","",":k:dispositions_k:reporter_phone:2"] } ] }
				]},
				{ div:["g"], arg:["","","activity_disposition_r_new_contact-dispositions-vftab-vdisp-!"] }, // vp return anchor
			]},
			
			{ div:["c xx g"], c:
			[
				{ input:["g","","activity_vw_vt3","1","radio"] },
				{ ac:["ay","case_uuid_new-cases_uuid","_activity_case","xx bd16 gg cw",""], c:
				[
					{ s:["c x t04 h2 b","+"] },
					{ s:["c x y s","New Case"] },
					{ div:["e"], arg:["","case_id","-1"] }
				]},
				{ div:["g"] } // arg:["","",""] }, // vp return anchor
			]},
			
			{ div:["c xx g"], c:
			[
				{ input:["g","","activity_vw_vt3","0","radio"] },
				{ ac:["ay","activity_disposition_new-cases_uuid-^","_activity_disposition_new","xx bd16 gg cw",""], c:
				[
					{ s:["c x t h2 b","#"] },
					{ s:["c x y s","Disposition"] },
					{ input:["g","","adt","2","radio",""] },
					{ div:["e"] }
				]},
				{ div:["g"], arg:["","","activity_disposition_r_new-dispositions-vftab-vdisp-!"] }, // vp return anchor
			]}, */

			{ div:["d w40 xx"], s:["xx yy bd ba",""], c:
			[
				{ s:["x y b","Reason for Calling"] },

				{ ac:["aa t02","","","x y gws bd","VAC"] },

				{ ac:["aa t02","","","x y gws bd","GBV"] },

				{ ac:["aa t02","","","x y gws bd","GIZ"] },

				{ ac:["aa t02","","","x y gws bd","Others"] },

				{ ac:["aa t02","","","x y gws bd","Followup"] },

			]},
			
			{ div:["e"] }
		]},
			
		{ div:["e"], c:[ { arg:["","","activity_match_list-dispositions"] }, { arg:["","","0"] }, { arg:["","","0"] }, { arg:["","",""] } ] }
	]},	

	{ div:["x25 t20 b10" ,"vf"], c:[ { div:["","activity_match_f-dispositions_f"], ev:["l__vpf"], c:
	[
		{ activity_match_f_tags_k:[] }
	]} ]},
	
	{ div:[], c:
	[
		{ div:[], c:
		[ 
			{ input:["g","","cghgmtv","0","radio","1"] }, 
			{ p:["tabvb r40 yy ","vs"], u:[null,null] } 
		]},
	]}
]};

te["activity_match_none"] = { activity_match_:["activity_match_list_none","activities"] };

te["activity_match"] = { activity_match_:["activity_match_list","dispositions_ctx"] };

te["activity_match_main"] = { c: // 
[
	{ div:[], c:
	[
		{ input:["g","","activity_vw_vt2","1","radio","1"] }, 
		{ p:["tabv ","vftab"], c:
		[
			{ arg:["",":v:activities:src::case_src:11",":v:activities:src_address"] },
			{ ufn:["activity_search_vw_ufn"] }
		]} 
	]},
	{ div:[], c:
	[	
		{ input:["g","","activity_vw_vt2","1","radio"] }, // case-form (new|followup)
		{ p:["tabv ","vfvw"] }
	]},
]};

// --------------------------------------------------------------------------------------------------------------------

te["activity_vw_id_tabs_"] = { c:
[
	{ div:[], c:
	[	
		{ input:["g","","activity_vw_vt","0","radio",null] }, // src
		{ p:["tabv","vt"], u:[null] } // vfls
	]},
	{ div:[], c:
	[	
		{ input:["g","","activity_vw_vt","0","radio",null] }, // profile
		{ p:["tabv mh90","vt"], u:[null] } 
	]}	
]};

te["activity_vw_id_match"] = { activity_vw_id_tabs_:["","noop","1","activity_match_main"] };

te["activity_vw_id_args"] = { c:[ { arg:["","src",":v:activities:src"] }, { arg:["","src_uid",":v:activities:src_uid"] }, { arg:["","src_address",":v:activities:src_address"] }, { arg:["","src_uid2",":v:activities:src_uid2"] }, { arg:["","src_usr",":v:activities:src_usr"] }, { arg:["","src_vector",":v:activities:src_vector"] }, { arg:["","src_callid",":v:activities:src_callid"] }, { arg:["","src_ts",":v:activities:src_ts"] } ] };

te["activity_vw_id"] = { c: 
[
	{ div:["t","vb"], c: 
	[
		/*
		{ div:["c"], c:
		[
                	{ input:["g","","avt","1","radio",null] },
			{ ac:["ay tab","","_tab","xx yy cb gws_",""], c:
			[	
				{ s:["c","Activities"] },
				{ div:["e"] }
			]},
		]},
		
		{ div:["c"], c:
		[
			{ input:["g","","avt","0","radio",null] },
			{ ac:["ay tab","","_tab","xx yy cb gws_",""], c:
			[
				{ span:["","",":v:activities:src_vector::vector:4"] },
				{ span:["l","",":v:activities:src::case_src:10"] },
			]},
		]}, */

		{ div:["c xx"], c:
		[
			{ input:["g","","avt","0","radio",null] },
			{ input:["g","","avt","0","radio",null] },
			{ ac:["ay","","","xx yy cb",""], c:
			[
				{ span:["","",":v:activities:src_vector::vector:4"] },
				{ span:["l","",":v:activities:src::case_src:10"] },
				{ span:["l","","Activity"] },
			]},
		]},
	
		{ p:["d w50 t","src_btns"], c:[ { div:["abs w50",":v:activities:src_uid"], u:[null] } ] }, 	// chan button
		
		{ div:["e"], c:[ { p:["g","o"], activity_vw_id_args:[] } ] },
	]}, 
	{ form:[""] } 	// tabs
]};

te["activity_btns"] = { c:
[	
	{ div:["d x"], c:
	[
		{ input:["g","","sbr","1","radio"] },
		{ ac:["x","","_activity_close","x cb",""], c:
		[
			{ s:["d x y h2 b","&Cross;"] },
			{ s:["d x y ","Close"] },
			{ div:["e"] }
		]},
	]},
		
	{ div:["e"] }
]};

te["activity_toolbar"] = { div:["ma w12 ","chan_id_here"], c: // 
[
	{ input:["g","","sbl","100","radio","1"] },
	{ ac:["abs mtn37 ao w12 sbl","","_activity_show","w12 bd tc cb gws_",""], c:[ { div:[""], c:
	[
		{ s:["x y tc",":v:activities:src::case_src:7"] },
	]} ]}
]};

// -----------------------------------------------------------------------------------------

te["activity_lst_footer"] = { div:["x y mt"], c:
[
	{ div:["d t03"], c:[ { ac:["nav","activity_lst-activities","_nav","dh",""], c:[ { div:["da dr_"] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] },
	{ div:["d t03"], c:[ { aci:["nav","activity_lst-activities","_nav","dh","prev",""], c:[ { div:["da dl_"] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] },
	{ s:["d l r15 y cd s","%4"] },
	{ s:["d  y cd s","of"] }, 
	{ s:["d x y cd s","%3"] },
	{ s:["d x y cd s","-"] },
	{ s:["d x y cd s","%2"] },
	{ div:["e"] }
]};

te["activity_lst_disposition_r"] = { div:["d ll y04 s cr"], uval:["","%0"] };

te["activity_lst_disposition"] = { uchk:["activity_lst_disposition_r","%0"] };

te["activity_lst_r"] = { div:[], c:
[
	{ input:["g","","sbl","1","radio"] },
	{ li:["sbr cb xx bb_",""], ev:["_activity_vw"], s:["x s y",""], c: 
	[
		{ div:[""], c:
		[
			{ div:[], c:
			[
				{ s:["c t",":v:activities:src_vector::vector:4"] },  
				{ s:["c t x",":v:activities:src::case_src:1"] },
				{ s:["c t",":v:activities:activity"] },
				{ s:["d t",":r::18:: : ago:: : ago:"] },
				{ arg:["tm","","%18"] },
				{ div:["e"] }
			]},
			{ div:[], c:
			[
				{ s:["c t",":v:activities:src_address"] },	
				{ s:["d t",":h:ms:24:0:"] },
				{ s:["d x t",":v:activities:src_status::activity_status:1"] }, 
				{ div:["e"] }
			]},
			{ p:["",":v:activities:src_uid"], c:
			[ 
				{ uchk:["activity_lst_disposition_r",":v:activities:dispositions"] }, 
				{ div:["e"] } 
			]}
		]},
		
		{ div:["e"], c:
		[ 
			{ arg:["",".id","%0"] }, { arg:["","src",":v:activities:src"] },
			{ arg:["","src_uid",":v:activities:src_uid"] }, { arg:["","src_uid2",":v:activities:src_uid2"] }, 
			{ arg:["","src_address",":v:activities:src_address"] }, { arg:["","src_usr",":v:activities:src_usr"] }, 
			{ arg:["","src_vector",":v:activities:src_vector"] },  { arg:["","src_ts",":v:activities:src_ts"] }, 
			{ arg:["","src_callid",":v:activities:src_callid"] } 
		]}
	]}
]};

te["activity_lst_k"] = { div:["g"], c:
[
	{ p:["","e"], c:[ { arg:["","_c","%1"] } ] }
]};

te["activity_lst_title"] = { div:["g x y bb_"], c:
[
	//{ div:["c","va"], ac:["","activity_lst-activities-vt","_u","xx yy cd","Activities"] },
	{ div:["e"] }
]};

te["activity_lst"] = { list:["activity_lst_title","end","","activity_lst_k","activity_lst_r","activities","activity_lst_footer"] }; // sbr panel

// -------------------------------------------------------------

te["activity_case_ufn"] = { ufn:["activity_case_ufn"] };

// -------------------------------------------------------------

function activity_messages_height (el, u, a, r, m)
{
	el.style.height = window.innerHeight-310;
	var h = el.scrollHeight;
	console.log (" [scroll height ] "+h);
	el.scroll ({ top: h, left: 0, behavior: 'smooth' }); 
}

function activity_messages_ufn (el, u, a, r, m)
{
	var p = el.nextSibling.firstChild; 
	var el = p.lastChild;
	var id = 0;
	if (p.lastChild && p.lastChild.firstChild) id = p.lastChild.firstChild.value*1;
	var rr = ra["messages"];
	var n = rr.length;
	for (var i=n-1; i>-1; i--)
	{
		var r = rr[i];
		if ((r[0]*1)<=id) continue;
		nd (p, te["activity_message_r"], [], r, [0]); // append new messages 
	}
	//console.log (" ---> "+el);
	for (var i=0; i<n; i++)	// update read status
	{
		var r = rr[i];
		//console.log (" ---> "+r[0]+","+el.firstChild.value + "|"+i+" of "+n)
		if (!el) break;
		if ((r[0]*1) > (el.firstChild.value*1)) continue;
		if ((r[0]*1) == (el.firstChild.value*1)) 
		{
			_(el,"tm","input").parentNode.firstChild.firstChild.innerHTML = r[15];
			el = el.previousSibling
		}
	}
	activity_messages_height (p, u, a, r, m);
}

function activity_message_sended (el, u, a, r, m)
{
	var p = __(el,"ve");
	var k = ra["messages_k"]
	var el = nd (el, te["activity_messages_txt"], [], [], [0]);
	el.focus (); // console.error (el.tagName)
	url (p.parentNode.firstChild, "activity_messages", "messages", ("?src="+r[k["src"][0]]+"&src_callid="+r[k["src_callid"][0]]+"&"));
}

function _activity_message_send (ev)
{
	var p = __(this,"ve");
	var p_ = __(this,"vfvwm");
	var o = {};
	jso (p_.firstChild, o);   	// channel session details
	jso (p,o); 			// ve details
	url (p, "activity_message_send", "messages", "", null, 2, o, "POST");
	boo (ev)
}

function _msg (ev)
{
	// console.error (ev.shiftKey+", "+ev.keyCode)
	if (ev.shiftKey==false && ev.keyCode==13)
	{
		this.disabled = true;
		var p = __(this,"ve");
		var p_ = __(this,"vfvwm");
		var o = {};
		jso (p_.firstChild, o);   	// channel session details
		jso (p,o); 			// ve details
		url (p, "activity_message_send", "messages", "", null, 2, o, "POST");
		return false;
	}
}
// -------------------------------------------------------------

function activity_search_vw_ufn (el, u, a, r, m)
{
	var k = re["activities_k"]["src_address"][0]; 
	var v = r[k]; 
	if (v.length>0) 
	{
		uv (el, ["activity_match","dispositions"], [], r, [0]) 
		return;
	}
	el.innerHTML = "";
	nd (el, te["activity_match_none"], [], [], [0]);
}

function activity_close ()
{
	var coll = document.getElementById ("vv").childNodes;	
	coll[1].innerHTML = ""; // toolbar
	coll[6].childNodes[1].childNodes[1].innerHTML = "";  	// vw
	coll[6].childNodes[10].firstChild.checked = true; 	// todo: show last tab b4 popup
	nd (coll[1], te["toolbar_default"], [], [], [0]); 	// show toolbar
	var p = document.getElementById ("vp"); 		// close vp (if open)
	p.style.display = "none";
	p.innerHTML = "";
}

function activity_disposition_ls (p)
{
	var a = {args:"?", _c:null, __c:null};
	argv (p.childNodes[1].firstChild, a);
	url (p, "activity_match_vw_f", "dispositions", a.args);
	// todo: update sbr
}

function activity_disposition_hangup (el) // add disposition to vw
{
	var p = __(el,"vfvwm")
	var callid = _(p,"src_btns").firstChild.firstChild;
	if (callid!=null && callid.value && callid.value.length>0) 
	{
		phone_hangup (callid.value);
		// activity_close (); b//btodo: bmark as bdoneb ob allowb tnex bpopup
	}
}

function activity_case_ufn (el, u, a, r, m)
{
	var p = el.parentNode.previousSibling;
	p.firstChild.checked = true;
	if (!ra["dispositions"] || ra["dispositions"].length<1) return;
	var p_ = _(p.childNodes[1],"vdisp");
	var el_ = document.createElementNS ("http://www.w3.org/1999/xhtml", "div");
	p_.insertBefore (el_, p_.firstChild);
	nd (el_, te["activity_disposition_r_new"], [], ra["dispositions"][0], [0]); // show toolbar	
}

function activity_postj (el, p__, o) 
{

}

function _activity_close (ev)
{
	activity_close ();
	boo (ev)
}

function _activity_case_postj (ev)
{
	var u = this.id.split ("-");
	var p = __(this, "ve");
	var p_ = __(elvp,"vfvw");
	var p__ = __(p_,"vfvwm");
	var o = {};
	var o_ = {};
	jso (p__.firstChild, o);  // channel details
	jso (p, o);
	jso (p_, o_);
	o["case_id"] = o_[".id"];
	url (p, u[0], u[1], o[".id"], null, 2, o, "POST");
}

function _activity_postj (ev)
{
	var u = this.id.split ("-");
	var p = __(this,"ve");
	var p__ = __(elvp,"vfvwm")
	var o = {};
	jso (p__.firstChild.lastChild, o); 	// channel data
	jso (p,o); 				// case details (including reporter|followup)
	url (p, u[0], u[1], o[".id"], null, 2, o, "POST");
	boo(ev); 
}

function _activity_case (ev)
{
	var u = this.id.split ("-");
	var o_ = {  };
	var o = { "contact_id":"-1", "case_id":"-1" };
	var p_ = __(this, "vf");
	var p = p_.id=="vftab" ? p_.parentNode.nextSibling : p_; // alert (p_.id)
	boo (ev);
	jso (__(p_,"vfvwm").firstChild, o);  	// channel data
	argv (p_, o_)				// contact_id (reporter)
	argv (this.firstChild.lastChild, o);	// case_id
	console.log (o)
	if (o["src"]=="edit")
	{
		if (u[0]=="case_uuid_update") 
		{
			p = document.getElementById ("vp");
			elvp = this.nextSibling;
			vp (p);
		}
		url (p, u[0], u[1], "", null, 0, o, "POST");
		return;
	}
	if (o_["activity_contact_id"]===undefined || (o_["activity_contact_id"]*1)<1)
	{
		var r_ = ["Select a Contact first / Create a Contact, before Creating a Case"];
		if ((o["case_id"]*1)>0) r_ = [("Select a Contact first Create a Contact, before Updating "+CASE_ID_PREFIX+o["case_id"])];
		p = document.getElementById ("vp");
		vp (p);
		nd (p, te["activity_contact_case_nb"], [], r_, [0]);
		return;
	}
	if (o_["activity_contact_id"]!=undefined) o["contact_id"] = o_["activity_contact_id"];
	o["reporters_uuid"] = { "f":"1" }; // api will create new reporter is this obj is there
	this.previousSibling.checked=true;
	p.firstChild.checked = true;
	p.childNodes[1].innerHTML = "";
	url (p.childNodes[1], u[0], u[1], "", null, 0, o, "POST");
}

function _activity_disposition_new (ev)
{
	var p = document.getElementById ("vp");
	var p_ = __(this, "vftab");
	var o_ = {};
	var o = { "contact_id":"-1", "case_id":"-1" };
	elvp = this.nextSibling;
	vp (p);
	jso (__(p_,"vfvwm").firstChild, o);  	// channel data
	argv (p_, o_)				// contact_id (reporter)
	if (o_["activity_contact_id"]) o["contact_id"] = o_["activity_contact_id"];
	url (p, "activity_disposition_new", "cases_uuid", "", null, 0, o, "POST");
	boo (ev);
}

function _activity_disposition_uvwr ()
{
	this.previousSibling.checked = true;
	var p = __(this,"va").parentNode;
	p.innerHTML = "";
}

function _activity_disposition_vwr (ev)
{
	var p = __(this,"vt").previousSibling.firstChild.firstChild;
	var a = {};
	argv (this, a);
	this.previousSibling.checked = true;
	url (p, "activity_disposition_vwr", "dispositions", a[".id"]);
}

function _activity_show ()
{
	var coll = document.getElementById ("vv").childNodes;
	this.previousSibling.checked = true;
	coll[6].childNodes[1].firstChild.checked = true;
}

function _activity_vw (ev) 
{
	var coll = document.getElementById ("vv").childNodes;
	var a = {};
	var r_ = re["r_"][0].slice(0);
	var k = re["activities_k"];
	var u = ["activity_vw_id_match","activities"];
	var s_ = "";
	argv (this, a);
	var u_ = re["case_src"][a.src];
	if (/*a.src=="walkin") && */ a.src_uid==undefined) // simulate chani 
	{ 
		var user_cid = document.getElementById ("user_cid").value;
		a.src_ts = Date.now()/1000;
		a.src_uid = a.src+"-"+user_cid+"-"+Date.now ();
		if (a.src_callid==undefined) a.src_callid = a.src_uid;
		// a.src_address = "";
		a.src_usr = user_cid
		a.src_vector = 0;
		a.src_uid2 = a.src_uid+"-2";
		if (a.src_callid) 
		{
			s_ = "&src_vector="+a.src_vector+"&src_callid="+a.src_callid;
			u_[9] = "activity_vw_id_messages_match";
		}
	}
	r_[k["src"][0]] = a.src;
	r_[k["src_ts"][0]] = a.src_ts;
	r_[k["src_uid"][0]] = a.src_uid;
	r_[k["src_callid"][0]] = a.src_callid;
	r_[k["src_address"][0]] = a.src_address;
	r_[k["src_usr"][0]] = a.src_usr;
	r_[k["src_vector"][0]] = a.src_vector;
	r_[k["src_uid2"][0]] = a.src_uid2;
	if (re["case_src"][a.src][11]=="reporter_phone") r_[k["src_address"][0]] = _phone_fmt (a.src_address);

	var s = a[".id"]+"?src=" + a.src + "&src_uid=" + a.src_uid + s_;
	if (r_[k["src_address"][0]].length>0)  
	{
		s += "&src_address="+r_[k["src_address"][0]];
	}
	
	this.previousSibling.checked = true; // hilite call-notif
	coll[1].innerHTML = ""; 			
	coll[6].childNodes[1].firstChild.checked = true;
	coll[6].childNodes[1].childNodes[1].innerHTML = "";

	nd (coll[1], te["activity_toolbar"], [], r_, [0]); // show toolbar	
	nd (coll[6].childNodes[1].childNodes[1], te["activity_vw_id"], ["activity_btns","","1"], r_, [3]);	
	url (coll[6].childNodes[1].childNodes[1].lastChild, u_[9], u[1], s);

	boo (ev)
}

