
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
		{ div:[], umime:["activity_message_r_v", ":v:messages:src_msg", ":v:messages:src_mime", ":v:messages:src"] },
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

// --------------------------------------------------------------------------------------------------------------------

te["activity_case_ufn"] = { ufn:["activity_case_ufn"] };

te["activity_disposition_ufn"] = { ufn:["activity_disposition_ufn"] };

te["activity_reporter_ufn"] = { ufn:["activity_reporter_ufn"] };

// ---

te["activity_contact_f"] = { div:["","ve"], c:                                                                                                 [
        { div:[], activity_f_:["y b","Search"] },
        { vp_apply_:["activity_contact_main-dispositions_f","_activity_uvpf","","_uvw"] }
]};

// ---

te["activity_contact_created_r"] = { c:
[
	{ div:["","va"], c:
	[
		{ s:["x y15 b","New Reporter"] },
		// todo: btns ?
		{ div:["e"] }
	]},
	{ div:[], c:
	[
		{ p:["","o"], c:
		[
			{ div:[], c:
			[
				{ input:["g","","contact_id",":v:contacts:id","radio","1"] },
				{ div:["r bt_"], ev:["_opt"], c:[ { li:["xx t02 bd cb rg"], c:
				[
					{ div:["c w01_ t08"], s:["opt",""] },
					{ div:["c w55"], contact_vw_rv:[":v:contacts:fullname", ":v:contacts:age_group", ":v:contacts:sex", "","", ":v:contacts:location",":v:contacts:landmark"] },
					{ ac:["d y ab","","","xx y03 bd gd cw","Edit"] },
					{ div:["e"] }
				]} ]},
			]},
			{ div:["y bt_"] }
		]}
	]}
]};

te["activity_contact_created"] = { c:
[
	{ ufn:["activity_src_address_ufn"] },
	{ u:["case_contact_new","contacts_src"] },
	{ ufn:["activity_contact_ufn"] } // switch to 'select contact' tab
]};

// ---

te["activity_contact_footer"] = { div:["xx b05"], c:
[
	{ div:["d t"], c:[ { ac:["nav","activity_contact_ls-dispositions","_nav","dh bd",""], c:[ { div:["da_w dr bd"] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] },
	{ div:["d t"], c:[ { aci:["nav","activity_contact_ls-dispositions","_nav","dh bd","prev",""], c:[ { div:["da_w dl bd"] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] },
	{ s:["d x y cd s","%4"] },
	{ s:["d y cd s","of"] }, 
	{ s:["d x y cd s","%3"] },
	{ s:["d x y cd s","-"] },
	{ s:["d x y cd s","%2"] },
	{ div:["e"] }
]};
	
te["activity_contact_no_data"] = { c:
[
	{ s:["xx yy gy","No matching contacts found."] }
]};

te["activity_contact_r"] = { div:[""], c:
[
	{ input:["g","","contact_id",":v:dispositions:reporter_contact_id","radio"] },
	{ div:["r h05 oh"], ev:["_opt"], c:[ { li:["x t02 cb rg"], c:
	[
		{ div:["c l w01_ t08"], s:["opt",""] },
		{ div:["c w59"], contact_vw_rv:[":v:dispositions:reporter_fullname", ":v:dispositions:reporter_age_group", ":v:dispositions:reporter_sex", "d x t cd s",":v:dispositions:created_on:d:dmyhnr", ":v:dispositions:reporter_location",":v:dispositions:reporter_landmark"] },
		{ div:["e"] }
	]} ]},
]};

te["activity_contact_k"] = { div:["g"], c:
[
	{ activity_disposition_k_:[] },
	{ arg:["","_c","%1"] },
	{ arg:["","sort","id"] },
	{ arg:["","group","reporter_contact_id"] },
	{ div:["e"] } 
]};
	 
te["activity_contact_nb"] = { div:[], c:
[
	{ u:["activity_contact_no_data","dispositions_no_data"] }
]};

te["activity_contact_ls"] = { listo:["end", "activity_contact_nb", "h25", "activity_contact_k", "activity_contact_r", "dispositions", "activity_contact_footer"] };

te["activity_contact_ls_main"] = { c:
[
	{ div:["x","va"], c:
	[
		{ s:["c yy b","Select Reporter"] },	
		{ div:["d l15 t"], c:
		[
			{ input:["g","","aca","2","radio"] },
			{ ac:["ay","","_vw","x t02 bd8 cb",""], c:
			[ 	
				{ s:["d r05 t03 s","New Reporter"] }, 
				{ s:["d x y03 b micon","add"] },
				{ div:["e"] }
			]}
		]},
		{ div:["d l15 t g"], c:
		[
			{ input:["g","","aca","1","radio"] },
			{ ac:["ay","","_vw","x t02 bd8 cb",""], c:
			[ 
				
				{ div:["d r05 t03 s","","Search"] }, 
				{ s:["d x y03 micon","search"] },
				{ div:["e"] }
			]}
		]},
		{ div:["e"] }
	]},
	{ div:["ba bd","vt"], activity_contact_ls:[] }
]};

te["activity_contact_error"] = { s:["xx y gp cr","Select a Reporter is required."] };

te["activity_contact_disposition"] = { div:["","ve"], c:
[
        { div:["gp"], c:[ { p:["","nb"] }, { div:["e"] } ] },
        { div:["","vt"], c:
        [
                { activity_f_tags:[] },
                { arg:["","_c","5"] },
                { arg:["","sort","id"] },
                { uv:["activity_contact_ls_main","dispositions"] }
        ]},
        { div:["t15 b10"], c:
        [
                // { p:["","o"], arg:["","case_id","-1"] },
                { ac:["ao btn t12","","_activity_reporter","y07 gb cw bd b n tc","Disposition"] }
        ]}
]};

te["activity_contact_main"] = { div:["","ve"], c:
[
	{ div:["gp"], c:[ { p:["","nb"] }, { div:["e"] } ] },
	{ div:["","vt"], c:
	[
		{ activity_f_tags:[] },
		{ arg:["","_c","5"] },
		{ arg:["","sort","id"] },
		{ uv:["activity_contact_ls_main","dispositions"] } 
	]},
	{ div:["t15 b10"], c:
	[
		{ p:["","o"], arg:["","case_id","-1"] },
		{ ac:["ao btn t12","","_activity_reporter","y07 gb cw bd b n tc","New Case"] }
	]}
]};

te["activity_contact_followup"] = { div:["","ve"], c:
[
        { div:["gp"], c:[ { p:["","nb"] }, { div:["e"] } ] },
        { div:["","vt"], c:
        [
                { activity_f_tags:[] },
                { arg:["","_c","5"] },
                { arg:["","sort","id"] },
                { uv:["activity_contact_ls_main","dispositions"] }
        ]},
        { div:["t15 b10"], c:
	[
		{ p:["","o"], arg:["","case_id",":k:dispositions_f:case_id"] },
                { ac:["ao btn","","_activity_reporter","y07 gb cw bd b n tc","Followup"] },
                { div:["e"] }
        ]}
]};

// ---

te["activity_disposition_ed_r"] = { div:["",""], c:
[
	{ input:["g","","disposition_id","%0","radio"] },
	{ div:["r ay bd_"], ev:["_opt"], c:[ { li:["xx t02 cb"], c:
	[
		{ div:["c w01_ t07"], s:["opt",""] },
		{ div:["c x y w50"], uval:["",":v:categories:fullname"] },
		{ div:["e"] }			
	]} ]}
]};

te["activity_disposition"] = { c:
[
        { s:["x yy b","Reporter"] },

        { div:["gp"], c:[ { p:["","nb"] }, { div:["e"] } ] },

        { div:["x yy"], c:
        [
                { contact_vw_rv:[":v:contacts:fullname", ":v:contacts:age_group", ":v:contacts:sex", "","", ":v:contacts:location",":v:contacts:landmark"] },
                { p:["","o"], arg:["","contact_id","%0"] }
        ]},

        { p:["h20 oy ba_ bd","o"], u:["activity_disposition_ed_r","subcategories"] }
]};

te["activity_disposition_new_contact"] = { c:
[
	{ arg:["",".id","%0"] },
	{ uv:["activity_disposition","contacts^disposition"] }
]};

te["activity_disposition_new_contact_unk"] = { c:
[
	{ s:["x yy b","Reporter not selected. (Enter Gender and Age Estimate.)"] },

	{ div:["gp"], c:[ { p:["","nb"] }, { div:["e"] } ] },

	{ div:["t"], c:
	[
		{ div:["c w20"], case_sex_enum:["Sex","","",""] },
		{ div:["c w21 ll"], case_contact_ed_age:["","","","","",""] },
		{ div:["e"] }
	]},

	{ div:["tt b20"], c:
	[
		{ div:["c w42"], case_loc_enum:["Location","","",""] },
		{ div:["e"] }
	]},
	
	{ p:["h20 oy ba_ bd","o"], c:
	[
		{ arg:["","_c","100"] },
		{ arg:["","root_id",DISPOSITION_ROOT_ID] },
		{ arg:["","level","1"] },
		{ uv:["activity_disposition_ed_r","subcategories"] }
	]}
]};

te["activity_disposition_new_"] = { div:["","ve"], c:
[
	{ div:[], c:
	[
		{ div:["abs tt"], ac:["ay","","_uvw","h3 x y bd16 cb micon","arrow_back"] },	
	]},

	{ div:["ml3"], u:[null] },

	{ div:["t15 b10 ml3"], c:
	[
		{ ac:["ao btn",null,"_activity_postj","y07 gb bd cw b n tc","Disposition"] },
		{ s:["y07 bd b tc gws_ bd savl","..."] }
	]}
]};

// ---

te["activity_new_"] = { div:["w64 x15 y ma sh__ gw_ bd8","vdd"], ev:["_undd"], c:
[
	{ div:[], c:
	[
		{ s:["c x t15 b10 h3 b",null] },
		{ ac:["d","","_uvp","x y h cb","&Cross;"] },
		{ p:["e","o"] } // , arg:["","case_id",null] }
	]},
	{ div:[], c:
	[
		{ div:[], c:		// select contact
		[
			{ input:["g","","activity_action_0","0","radio","1"] },
			{ div:["tabv","vf"], u:[null] }
		]},
		{ div:[], c:		// search contact
		[
			{ input:["g","","activity_action_0","0","radio"] },
			{ div:["tabv x","vf"], activity_contact_f:[] }
		]},
		{ div:[], c:		// new contact
		[
			{ input:["g","","activity_action_0","0","radio"] },
			{ div:["tabv x","vf"], c:
			[
				{ ufn:["activity_src_address_ufn"] },
				{ u:["case_contact_new","contacts_src"] }
			]}
		]},
		{ div:[], c:		// disposition
		[
			{ input:["g","","activity_action_0","0","radio"] },
			{ div:["tabv x","vf"] }
		]}
	]}
]};

te["activity_new_disposition"] = { activity_new_:["Disposition","activity_contact_disposition"] };

te["activity_new"] = { activity_new_:["New Case","activity_contact_main"] };

te["activity_followup"] = { activity_new_:["Followup Activity","activity_contact_followup"] };

// ---

te["activity_disposition_vwr_case"] = { c:
[
	{ div:["tt"], c:
	[
		{ s:["c x y b",CASE_ID_PREFIX] },
		{ s:["c y b",":v:cases:id"] },
		{ div:["e"] }
	]},
	{ div:["tt"], c:
	[
		{ s:["x t cd","Case Category"] },
		{ div:["x t"], uval:["",":v:cases:case_category"] },
		{ div:["e"] }
	]},
	{ div:["tt"], c:
	[
		{ s:["x t cd","Case Narrative"] },
		{ div:["x t"], s:["",":v:cases:narrative"] },
		{ div:["e"] }
	]},
	{ div:["tt"], c:
	[
		{ s:["x t cd","Case Plan"] },
		{ div:["x t"], s:["",":v:cases:plan"] },
		{ div:["e"] }
	]},
	{ div:["tt"], c:
	[
		{ s:["c x t cd","Priority"] },
		{ s:["d x t cd","Status"] },
		{ div:["e"] }
	]},
	{ div:[""], c:
	[
		{ div:["c x t"], s:["",":v:cases:priority::case_priority:2"] },
		{ div:["d x t"], s:["",":v:cases:status::case_status:1"] },
		{ div:["e"] }
	]},
	
	{ div:[], usub:["case_vw_refered_to_none,case_vw_refered_to_dept_sub,case_vw_refered_to_sub","cases",":v:cases:is_refered_to","0,1,2"] },

	{ div:[], usub:["case_vw_escalated_to_sub","cases",":v:cases:is_escalated_to","1"] } 
]};

te["activity_disposition_vwr_contact"] = { c:
[
        { div:["t n"], c:
	[
		{ s:["c b r05",":v:contacts:fullname"] },
		{ div:["c xx"], uval:["",":v:contacts:sex"] },
		{ div:["c"], uval:["",":v:contacts:age_group"] },
		{ div:["e"] }
	]},
	{ div:["t15 s"], c:
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
	{ div:["tt"], c:
	[
		{ s:["c w03 micon h3","call"] },
		{ s:["c ",":v:contacts:phone"] },
		{ s:["c xx ",":v:contacts:phone2"] },
		{ div:["e"] }
	]},
	{ div:["tt"], c:
	[
		{ s:["c w03 micon h3","email"] },
		{ s:["c",":v:contacts:email"] },
		{ div:["e"] }
	]},
]};

te["activity_disposition_vwr"] = { div:["w64 x15 y15 ma sh__ gw_ bd8","vddvw"], ev:["_undd"], c:
[
	{ div:["xx","va"], u:["activity_disposition_vwr_contact","contacts"] },
	{ div:["x yy","va"], u:["activity_disposition_vwr_case","cases_related"] } 
]};

// ---

te["activity_disposition_footer"] = { div:["x20 t20 b10"], c:
[
	{ pg:["pgto","activity_disposition_list-dispositions"," dh","da dl","activity_disposition_list-dispositions"," dh","da dr"] },
	{ div:["e"] }
]};

te["activity_disposition_rv_case"] = { c:
[
	{ s:["c l t",CASE_ID_PREFIX] },
	{ s:["c x t",":v:dispositions:case_id"] },
	{ div:["c l15 y02"], uval:["",":v:dispositions:case_category"] },
	// { s:["c x20 t cd",":v:dispositions:case_priority::case_priority:2"] },
	// { s:["c t cd",":v:dispositions:case_status::case_status:1"] },
	{ div:["e"] }
]};

te["activity_disposition_r_"] = { c:
[
	{ div:["abs xx tt"], s:["x y micon h3 ba gws_ bd16",":v:dispositions:src::case_src:6"] },
	{ div:["ml2_ mh05 x30 yy bl r"], c:
	[
		{ div:[], c:
		[
			{ div:["c x t"], s:[null,""], uval:["",":v:dispositions:disposition"] },	
			{ u:[":u::57:0:noop:activity_disposition_rv_case"] },
			{ div:["e"] }	
		]},
		{ div:[null], c:
		[
			{ div:["c x t"], s:["",":v:dispositions:reporter_fullname"] },
			{ div:["c x t"], uval:["",":v:dispositions:reporter_sex"] },
			{ div:["c x t"], uval:["",":v:dispositions:reporter_age_group"] },
			{ div:["e"] }	
		]},
		{ div:["cd"], c:
		[
			{ s:["c l y",":r::1:: : ago:: : ago:"] },
			{ arg:["tm","","%1"] },
			{ s:["c x20 y",":v:dispositions:created_by"] },
			{ div:["e"] }	
		]}
	]},
	{ div:["e"], c:
	[
		{ arg:["","case_id",":v:dispositions:case_id"] }
	]}
]};

te["activity_disposition_r_case_"] = { div:["","va"], c:
[
        { input:["g","","advwt","%0","radio"] },
	{ li:[null,"activity_followup-dispositions_f"], ev:["_activity_new"], activity_disposition_r_:["b",""] },
        { div:["g"], arg:["","","activity_disposition_r-dispositions-va--@"] }, // vp return anchor
]};

te["activity_disposition_r_dsp_"] = { div:["","va"], c:
[
        // { input:["g","","advwt","%0","radio"] },
        { div:[null], activity_disposition_r_:["",""] }
]};

te["activity_disposition_r_case_new"] = { activity_disposition_r_case_:["xx lr gh"] };

te["activity_disposition_r_dsp_new"] = { activity_disposition_r_dsp_:["xx lr gy cd"] };

te["activity_disposition_r_case"] = { activity_disposition_r_case_:["xx lr"] };

te["activity_disposition_r_dsp"] = { activity_disposition_r_dsp_:["xx lr cd"] };

te["activity_disposition_r"] = { u:[":u::57:0:activity_disposition_r_dsp:activity_disposition_r_case"] };

//te["activity_disposition_r_new"] = { activity_disposition_r_:["l gh lr","ml2_ mh05 x30 yy bl r"] };

te["activity_disposition_k_"] = { c:
[
	{ arg:["","reporter_fullname",		":k:dispositions_k:reporter_fullname:2"] },
	{ arg:["","reporter_age_group_id",	":k:dispositions_k:reporter_age_group_id:2"] },
	{ arg:["","reporter_sex_id",		":k:dispositions_k:reporter_sex_id:2"] },
	{ arg:["","reporter_phone",		":k:dispositions_k:reporter_phone:2"] },
	{ arg:["","reporter_email",		":k:dispositions_k:reporter_email:2"] },
	{ arg:["","reporter_location_id",	":k:dispositions_k:reporter_location_id:2"] },
	{ arg:["","disposition_id",       	":k:dispositions_k:disposition_id:2"] },

	{ arg:["","case_id",			":k:dispositions_k:case_id:2"] },
	{ arg:["","cases^created_on",		":k:dispositions_k:cases^created_on:2"] },
	{ arg:["","cases^created_by_id",	":k:dispositions_k:cases^created_by_id:2"] },
	{ arg:["","src",			":k:dispositions_k:src:2"] },
	{ arg:["","cases^case_category_id",	":k:dispositions_k:cases^case_category_id:2"] },
	{ arg:["","cases^gbv_related",		":k:dispositions_k:cases^gbv_related:2"] },
	{ arg:["","cases^priority",		":k:dispositions_k:cases^priority:2"] },
	{ arg:["","cases^status",		":k:dispositions_k:cases^status:2"] },
	{ arg:["","cases^escalated_to_id",	":k:dispositions_k:cases^escalated_to_id:2"] },
	{ arg:["","cases^assessment_id",	":k:dispositions_k:cases^assessment_id:2"] },
	{ arg:["","cases^justice_id",		":k:dispositions_k:cases^justice_id:2"] },
]};

te["activity_disposition_k"] = { div:["g"], c:
[
	{ activity_disposition_k_:[] },
	{ arg:["","sort","id"] },
	{ arg:["","_c","%1"] }, 
	{ div:["e"] }
]};

te["activity_disposition_no_data"] = { div:[""], s:["x20 yy gy","No records found"] };

te["activity_disposition_nb"] = { div:[""], u:["activity_disposition_no_data","dispositions_no_data"] };

te["activity_disposition_title"] = { div:[], c:[ { p:["","vdisp"] } ] };

te["activity_disposition_list"] = { list:["activity_disposition_title", "activity_disposition_nb", "", "activity_disposition_k", "activity_disposition_r", "dispositions", "activity_disposition_footer"] };

// -----------------------------------------------------------------------------------------

te["activity_f_tags_"] = { c: 
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
	
	{ p:["g","o"], c:
	[
		{ arg:["","disposition_id",null] },
		{ arg:["","sort","id"] },
		{ arg:["","group",null] }
	]},
	{ div:["e"] }
]};
	
te["activity_f_tags_k"] = { activity_f_tags_:
[
":k:dispositions_k:reporter_fullname:2",":k:dispositions_k:reporter_age_group_id:2", 	":k:dispositions_k:reporter_sex_id:2", 
":k:dispositions_k:reporter_phone:2", 	":k:dispositions_k:reporter_email:2", 		":k:dispositions_k:reporter_location_id:2",
":k:dispositions_k:case_id:2", 		":k:dispositions_k:cases^created_on:2", 	":k:dispositions_k:cases^created_by_id:2", 
":k:dispositions_k:src:2", 		":k:dispositions_k:cases^case_category_id:2", 	":k:dispositions_k:cases^gbv_related:2",
":k:dispositions_k:cases^priority:2", 	":k:dispositions_k:cases^status:2", 		":k:dispositions_k:cases^escalated_to_id:2", 
":k:dispositions_k:cases^assessment_id:2",":k:dispositions_k:cases^justice_id:2",   
":k:dispositions_k:disposition_id:2",
""
]};
	
te["activity_f_tags"] = { activity_f_tags_:
[
":k:dispositions_f:reporter_fullname", 	":k:dispositions_f:reporter_age_group_id", 	":k:dispositions_f:reporter_sex_id",
":k:dispositions_f:reporter_phone", 	":k:dispositions_f:reporter_email", 		":k:dispositions_f:reporter_location_id",
":k:dispositions_f:case_id", 		":k:dispositions_f:cases^created_on", 		":k:dispositions_f:cases^created_by_id", 
":k:dispositions_f:src", 		":k:dispositions_f:cases^case_category_id", 	":k:dispositions_f:cases^gbv_related", 
":k:dispositions_f:cases^priority", 	":k:dispositions_f:cases^status", 		":k:dispositions_f:cases^escalated_to_id",  
":k:dispositions_f:cases^assessment_id",":k:dispositions_f:cases^justice_id",  
":k:dispositions_f:disposition_id",
":k:dispositions_f:group"
]};
	
te["activity_cases_f"] = { c:
[
	{ div:["l r10 tt"], kf_s:["Case ID","case_id",":k:dispositions_f:case_id"] },			
			
	{ div:["l r10 tt"], kf_d:["Created On"," :d:dmy:0: ","cases^created_on",":k:dispositions_f:cases^created_on","cases^created_on",":k:dispositions_f:cases^created_on"] },
			
	{ div:["l r10 tt"], kf_l:["Created By","tag_-r_--o--%5-user_id-cases^created_by_id-%0-%5",   "user_lc_main-users",":k:dispositions_f:cases^created_by_id", 
""," %1","user_id","cases^created_by_id"," %0"," %1",  "noop"] },

	{ div:["l r10 tt"], kf_c:["Source","tag_-r_--o--::case_src:0:1--src-%0-",  	":k:dispositions_f:src",
""," %0","","src"," %0","", 				":k:dispositions_f:src","case_src", "src"," %0",""] },
		
	{ div:["l r10 tt"], kf_l:["Category","tag_-r_--o--%1-category_id-cases^case_category_id-%0-%1",   "case_category_lc_main-subcategories",  ":k:dispositions_f:cases^case_category_id",  ""," %1","category_id","cases^case_category_id"," %0"," %1", "case_category_root_id"] },
	
	{ div:["l r10 tt"], kf_c:["GBV Related", "tag_-r_--o--::yesno:0:2--cases^gbv_related-%0-",  ":k:dispositions_f:cases^gbv_related",
""," ::yesno:0:2","","cases^gbv_related"," %0","",       ":k:dispositions_f:cases^gbv_related","yesno",  "cases^gbv_related"," ::yesno:0:2",""] },

	{ div:["l r10 tt"], kf_c:["Priority", "tag_-r_--o--::case_priority:0:1--cases^priority-%0-",  ":k:dispositions_f:cases^priority", 
""," ::case_priority:0:1","","cases^priority"," %0","", 	":k:dispositions_f:cases^priority","case_priority",  "cases^priority"," ::case_priority:0:1",""] },
				
	{ div:["l r10 tt"], kf_c:["Status", "tag_-r_--o--::case_status:0:1--cases^status-%0-",  	":k:dispositions_f:cases^status",
""," ::case_status:0:1","","cases^status"," %0","", 	":k:dispositions_f:cases^status","case_status",  "cases^status"," ::case_status:0:1",""] },
		
	{ div:["l r10 tt"], kf_l:["Escalated To","tag_-r_--o--%5-user_id-cases^escalated_to_id-%0-%5",   "user_lc_main-users", ":k:dispositions_f:cases^escalated_to_id", 
""," %1","user_id","cases^escalated_to_id"," %0"," %1", "noop"] },

	{ div:["l r10 tt"], kf_l:["Case Assessment","tag_-r_--o--%1-category_id-cases^assessment_id-%0-%1",   "case_lc_main-subcategories", ":k:dispositions_f:cases^assessment_id", 
"", " %1", "category_id", "cases^assessment_id"," %0"," %1", "case_assessment_root_id"] },	

	{ div:["l r10 yy"], kf_l:["Status in Justice System","tag_-r_--o--%1-category_id-cases^justice_id-%0-%1",   "case_lc_main-subcategories", ":k:dispositions_f:cases^justice_id", 
""," %1","category_id","cases^justice_id"," %0"," %1", "case_justice_root_id"] },		
					
]};
	
te["activity_contacts_f"] = { c:
[
	{ div:["l r10 tt"], kf_s:["Reporter Name","reporter_fullname",":k:dispositions_f:reporter_fullname"] },
	
	{ div:["l r10 tt"], kf_l:["Reporter Age","tag_-r_--o--%1-category_id-reporter_age_group_id-%0-%1", "case_lc_main-subcategories", 
":k:dispositions_f:reporter_age_group_id", ""," %1","category_id","reporter_age_group_id"," %0"," %1", "case_age_group_root_id"] },

	{ div:["l r10 tt"], kf_l:["Reporter Sex","tag_-r_--o--%1-category_id-reporter_sex_id-%0-%1", "case_lc_main-subcategories",  
":k:dispositions_f:reporter_sex_id", ""," %1","category_id","reporter_sex_id"," %0"," %1", "case_sex_root_id"] },

	{ div:["l r10 tt"], kf_s:["Reporter Phone","reporter_phone",":k:dispositions_f:reporter_phone"] },
	
	{ div:["l r10 tt"], kf_s:["Reporter Email","reporter_email",":k:dispositions_f:reporter_email"] },
	
	{ div:["l r10 yy"], kf_l:["Reporter Location","tag_-r_--o--%1-category_id-reporter_location_id-%0-%1", "case_location_lc_main-subcategories",  ":k:dispositions_f:reporter_location_id", ""," %1","category_id","reporter_location_id"," %0"," %1", "case_location_root_id"] },

	{ div:["l r10 tt"], kf_s:["Passport/ID Number","reporter_national_id",":k:dispositions_f:reporter_national_id"] },

]};
	
te["activity_f_"] = { c:
[
	{ div:["t","vb"], c:
	[
		{ div:["c"], s:[null,null] },
		{ div:["d xx"], c:[ { input:["g","","case_f_vw_t","1","radio"] }, { ac:["ay tabu","","_tab","x03 y cb s","Cases"] } ] },
		{ div:["d xx"], c:[ { input:["g","","case_f_vw_t","0","radio","1"] }, { ac:["ay tabu","","_tab","x03 y cb s","Contacts"] } ] },
		{ div:["e"] }
	]},
	{ div:["yy"], c:
	[
		{ div:[], c:[ { input:["g","","case_f_vw_tv","0","radio","1"] }, { div:["tabv"], activity_contacts_f:[] } ] },
		{ div:[], c:[ { input:["g","","case_f_vw_tv","1","radio"] }, { div:["tabv"], activity_cases_f:[] } ] },		
		{ p:["","o"], arg:["","disposition_id",":k:dispositions_f:disposition_id"] }
	]}
]};
	
te["activity_f"] = { div:["w50 x15 tt b05 ma sh__ gw_ bd8","vddvf"], ev:["_undd"], c: 
[
	//{ div:[], c:
	//[
	//	{ s:[" c x t15 b05 h3 b","Search Activities"] },
	//	// todo: close
	//	{ div:["e"] }
	//]},
	{ div:[], activity_f_:["x y b h3","Search"] },
	{ vp_apply:["activity_f_tags-dispositions_f"] }
]};
	
te["activity_list"] = { c:
[
        { div:[], c:
        [
                { div:["d w55"], s:["w55 abs gws",""] }, // todo summary stats
                { div:["e"] }
        ]},
        { div:["x","vt"], u:["activity_disposition_list","dispositions_ctx"] }
]};

te["activity_main"] = { c: 
[
	{ div:["x t","vb"], c:
	[
		{ div:["c"], c:
		[
			{ div:["","va"], s:["",""], c:
			[
				{ input:["g","","cases_t_","0","radio","1"] },
				{ ac:["c x","activity_match-activities-vftab","___u","xx y b n cb","Activity History"] }, 	
				{ div:["e"] }
			]}
		]},		
		
		{ div:["c "], c:
		[
			{ ac:["ay","activity_f-dispositions_f","_vpf","xx bd16 cb",""], c:
			[ 
				{ s:["c y h3_ b micon","search"] },
				//{ div:["c x y s","","Search"] }, 
				{ div:["e"] }
			]}
		]},
		
		{ div:["c l25"], c: 
		[
			{ div:[], c:
			[
				{ input:["g","","activity_vw_vt_ss","0","radio","1"] },
				{ ac:["ay tabv","activity_new-dispositions_f","_activity_new","xx bd16 gws_ cb",""], c:
				[
					{ s:["c x t04 h2 b","+"] },
					{ s:["c x y s","New Case"] },
					{ div:["e"], c:
					[
						// { arg:["","disposition_id",(DISPOSITION_ID_CONTACT_NEW+","+DISPOSITION_ID_CONTACT_EDIT)] }
					]}
				]},
				{ div:["g"] } // arg:["","",""] }, // vp return anchor
			]},
			{ div:[], c:
			[
				{ input:["g","","activity_vw_vt_ss","1","radio"] },
				{ ac:["ay tabv","","_vw","xx bd16 co gws_",""], c:
				[
					{ s:["c x t04 h2 b","+"] },
					{ s:["c x y s","New Case In Progress ..."] },
					{ div:["e"] }
				]},
				{ div:["g"] } // arg:["","",""] }, // vp return anchor
			]},
			{ div:[], c:
                        [
                                { input:["g","","activity_vw_vt_ss","1","radio"] },
                                { ac:["ay tabv","","_vw","xx bd16 co gws_",""], c:
                                [
                                        { s:["c x t04 h2 b","+"] },
                                        { s:["c x y s","Followup In Progress ..."] },
                                        { div:["e"] }
                                ]},
                                { div:["g"] } // arg:["","",""] }, // vp return anchor
                        ]}
		]},

		{ div:["c x25"], c:
		[
			{ input:["g","","activity_vw_vt3","0","radio"] },
			{ ac:["ay","activity_new_disposition-dispositions_f","_activity_new","xx bd16 gws_ cb",""], c:
			[
				{ s:["c x t h2 b","#"] },
				{ s:["c x y s","Disposition"] },
				// { input:["g","","adt","2","radio",""] },
				{ div:["e"], c:
				[
					 // { arg:["","disposition_id",(DISPOSITION_ID_CONTACT_NEW+","+DISPOSITION_ID_CONTACT_EDIT)] }
				]}
			]},
			{ div:["g"] } //, arg:["","","activity_disposition_r_new-dispositions-vftab-vdisp-!"] }, // vp return anchor
		]},
				
		{ div:["e"], c:[ { arg:["","","activity_list-dispositions"] }, { arg:["","","0"] }, { arg:["","","0"] }, { arg:["","",""] } ] }
	]},	

	{ div:["x15 yy" ,"vf"], c:[ { div:["","activity_disposition_f-dispositions_f"], ev:["l__vpf"], c:
	[
		{ activity_f_tags_k:[] }
	]} ]},
	
	{ div:[], c: 
	[
		{ div:[], c:
		[ 
			{ input:["g","","cghgmtv","0","radio","1"] }, 
			{ p:["tabv","vt"], u:["activity_list","dispositions_ctx"] } 
		]},
		{ div:[], c:
		[	
			{ input:["g","","cghgmtv","0","radio"] }, 	// activity history rpt
			{ p:["tabv","vt"] } 
		]}
	]}
]};

// -----------------------------------------------------------------------------------------

te["activity_vw_id_args"] = { c:
[
    { arg:["","src",":v:activities:src"] },
    { arg:["","src_uid",":v:activities:src_uid"] },
    { arg:["","src_address",":v:activities:src_address"] },
    { arg:["","src_uid2",":v:activities:src_uid2"] },
    { arg:["","src_usr",":v:activities:src_usr"] },
    { arg:["","src_vector",":v:activities:src_vector"] },
    { arg:["","src_callid",":v:activities:src_callid"] },
    { arg:["","src_ts",":v:activities:src_ts"] }
]};

te["activity_toolbar"] = { div:["ma w12 ","chan_id_here"], c: // 
[
	{ input:["g","","sbl","100","radio","1"] },
	{ ac:["abs mtn37 ao w12 sbl bd","","_activity_show","w12 bd tc cb bd gws_",""], c:[ { div:[""], c:
	[
		{ s:["x y tc",":v:activities:src::case_src:1"] },
	]} ]}
]};

te["activity_vw_id_tabs_"] = { c:
[
	{ div:[], c:
	[	
		{ input:["g","","activity_vw_vt","0","radio",null] }, 	// activity history list
		{ p:["tabv","vf"], c:
		[
			{ arg:["",":v:activities:src::case_src:12",":v:activities:src_address"] },
			{ arg:["",":v:activities:src_address:z:zz:id","-1"] }, // if src is blank then id=-1
			{ uv:["activity_main","dispositions"] }
		]} 
	]},
	{ div:[], c:
	[	
		{ input:["g","","activity_vw_vt","0","radio"] }, 	// case_form | case_vw_id
		{ p:["tabv","vf"] } 
	]},
	{ div:[], c:
	[	
		{ input:["g","","activity_vw_vt","0","radio",null] }, 	// chat
		{ p:["tabv mh90","vf"], activity_messages:[] } 
	]}	
]};

te["activity_vw_id_tabs"] = { activity_vw_id_tabs_:["1",""] };

te["activity_vw_id_tabs_message"] = { activity_vw_id_tabs_:["","1"] };

te["activity_vw_id_tabs_call"] = { activity_vw_id_tabs_:["1",""] };

te["activity_vw_id"] = { c: 
[
	{ div:["l15 y15","vb"],  s:["",""], c: 
	[
		{ div:["c"], c:
		[
			{ input:["g","","avt","0","radio"] },
			{ ac:["","","_tab","x t08 cb h3 b",""], c:
			[
				{ span:["","",":v:activities:src::case_src:10"] },
				//{ span:["","",":v:activities:src_vector::vector:4"] },
			]},
		]},
	
		// { div:["c l tt g"], s:["h02 w02 awR",""] },

		{ div:["c"], c:
		[
			{ input:["g","","avt","0","radio"] },
			{ ac:["ay","","","xx yy cb h3 cd",""], c:
			[
				{ span:["","",""] },
			]},
		]},

		{ div:["d x"], c:
		[
			{ input:["g","","sbr","1","radio"] },
			{ ac:["x ay","","_activity_close","x cb t01 bd",""], c:
			[
				{ s:["d x h b","&Cross;"] },
				// { s:["d x y s","Close"] },
				{ div:["e"] }
			]},
		]},
		
		{ div:["d"], c:
		[
			{ input:["g","","activity_vw_id_t_","2","radio",null] },
			{ ac:["ay tab","","_tab","xx y gws_ bdr cb",""], c:
			[
				{ s:["c h2 micon","chat"] },
				{ div:["e"] }
			]}
		]},
		
		{ div:["d"], c:
		[
			{ input:["g","","activity_vw_id_t_","0,1","radio",null] },
			{ ac:["ay tab","","","xx y gws_ cb",""], c: // todo: show sub ie: [0,1]
			[
				{ s:["c h2 micon","bar_chart"] },
				{ div:["e"] }
			]}
		]},
		
		{ div:["d activity_tab_0_ l30"], c:
		[
			{ input:["g","","activity_vw_id_t_","0","radio",null] }, // [0,0] | [1]
			{ ac:["ay tab","","_tab","xx y gws_ bdl cb",""], c:
			[
				{ s:["c h2 micon","list"] },
				{ div:["e"] }
			]}
		]},

		{ u:[null] },

		{ div:["e"], c:[ { p:["g","o"], activity_vw_id_args:[] } ] }
	]}, 
	{ form:[] } 		// tabs
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
	{ input:["g","","sbr","1","radio"] },
	{ li:["sbr cb xx bb_",""], ev:["_activity_vw_id"], s:["x y s",""], c: 
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

function activity_messages_height (el, u, a, r, m)
{
	el.style.height = window.innerHeight-260;
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

function activity_close ()
{
	var coll = document.getElementById ("vv").childNodes;	
	coll[1].innerHTML = ""; 				// toolbar
	coll[6].childNodes[1].childNodes[1].innerHTML = "";  	// vw
	coll[6].childNodes[10].firstChild.checked = true; 	// todo: show last tab b4 popup
	nd (coll[1], te["toolbar_default"], [], [], [0]); 	// show toolbar
	var p = document.getElementById ("vp"); 		// close vp (if open)
	p.style.display = "none";
	p.innerHTML = "";
}

function activity_disposition_ufn (el, u, a, r, m)
{
	var el = document.createElementNS ("http://www.w3.org/1999/xhtml", "div");
	var p = document.getElementById ("vp");
	p.style.display = "none";
	p.innerHTML = "";
	p = elvpf.nextSibling.  firstChild.childNodes[1].childNodes[1].childNodes[1];
	p.insertBefore (el, p.firstChild);
	nd (el, te["activity_disposition_r_dsp_new"], [], r, [0]);
	// todo: update title with contact_id (if exists)
}

function activity_case_ufn (el, u, a, r, m)
{
	var coll = __(el,"vf").parentNode.previousSibling.childNodes;
	// coll[0].checked = true;
	if (coll[0].name=="case_vw_vt") 
	{
		var p = __(el,"vf");
		p.innerHTML = "";
		nd (p, te["case_vw_id"], [], ra["cases"][0], [0]);
		
		p = coll[1].childNodes[2].firstChild.childNodes[1].childNodes[2]
		var a = {}; 
		var b = {};
		argv (p.childNodes[1], a, "name", null, b);  // find checked row
		var el_ = b["casevwr"][0].parentNode;
		el_.innerHTML = ""
		nd (el_, te["case_r_"], ["gh cb","1"], ra["cases"][0], [2])
		return;
	}
	coll[0].checked = true;
	var el_ = document.createElementNS ("http://www.w3.org/1999/xhtml", "div");
	var p = coll[1].childNodes[2].firstChild.childNodes[1].childNodes[1].childNodes[1];
	p.insertBefore (el_, p.firstChild);
	nd (el_, te["activity_disposition_r_case_new"], [], r, [0]);
	coll[1].firstChild.childNodes[2].firstChild.firstChild.checked = true; 		// toggle new-case btn 
}

function activity_reporter_ufn (el, u, a, r, m)
{
	var coll = elvpf.parentNode.parentNode.nextSibling.childNodes;
	var p = document.getElementById ("vp");
	var u_= [["case_new","r_"],["case_vw_id","cases"]];
	var k = 0;
	if (ra["cases"] && ra["cases"][0] && (ra["cases"][0][0]*1)>0) k=1;
	p.style.display = "none";
	p.innerHTML = "";
	coll[0].checked = true;
	coll[1].innerHTML = "";
	nd (coll[1], te[u_[k][0]], [], ra[u_[k][1]][0], [0]);
	k++;
	elvpf.previousSibling.childNodes[2].childNodes[k].firstChild.checked = true; 		// toggle new-case btn 
	// todo: update title with contact_id
}

function activity_contact_ufn (el, u, a, r, m)
{
	var coll = el.parentNode.parentNode.firstChild.childNodes;
	coll[0].checked = true;	
	coll[1].firstChild.childNodes[1].innerHTML = "";
	nd (coll[1].firstChild.childNodes[1], te["activity_contact_created_r"], [], r, [0]);
	// todo: update title with contact
}

function activity_src_address_ufn (el, u, a, r, m)
{
	var j_ = -1;
	var k_ = re["contacts_k"];
	var v_ = "";
	var r_ = re["r_"][0].slice(0);
	var o = {};
	jso (__(elvpf,"vfvwm").firstChild, o); 		// src
	console.log (o)
	j_ = re["case_src"][o.src][11];
	v_ = o.src_address;
	console.log ("--->"+o.src+"|"+j_);
	if (j_=="phone") v_= _phone_fmt (o.src_address);
	r_[k_[j_][0]] = v_;
	ra["contacts_src"] = [r_];
}

function _activity_close (ev)
{
	activity_close ();
	boo (ev)
}

function _activity_uvw (ev)
{
	var coll = __(this,"vf").parentNode.parentNode.firstChild.childNodes;
	coll[0].checked = true;
	coll[1].firstChild.childNodes[2].firstChild.firstChild.checked = true;
}

function _activity_postj ()
{
	var u = this.id.split ("-");
	var p = __(this,"ve"); 
	var o = {};
	jso (__(elvpf?elvpf:(elvp?elvp:p),"vfvwm").firstChild, o);			// src
	jso (p, o); 									// form
	url (p, u[0], u[1], o[".id"], null, 2, o, "POST");
}

function _activity_reporter ()
{
	var p = null;
	var o = {};
	jso (__(this,"ve"), o);				// contact_id
	jso (__(elvpf,"vfvwm").firstChild, o); 		// src

	if (!o["case_id"] || (o["case_id"]*1)==0)
	{
		p = __(this,"vf").parentNode.parentNode.lastChild;
		p.firstChild.checked = true;
        	p.childNodes[1].innerHTML = "";
		var a = ["activity_disposition_unk-dispositions^unk","activity_disposition_new_contact_unk"];
		var r = [""]
		if (o["contact_id"] && (o["contact_id"]*1)>0) 
		{
			a = ["activity_disposition-dispositions","activity_disposition_new_contact"];
			r = [o["contact_id"]];
		}
		nd (p.childNodes[1], te["activity_disposition_new_"], a, r, [2]);
		return;
	}
		
	if (!o["contact_id"] || (o["contact_id"]*1)<1) 
	{
		p = _(__(this,"ve"),"nb");
		p.innerHTML = "";
		nd (p, te["activity_contact_error"], [],[],[0]);    
		return; 
	}
		
	url (__(this,"ve"), "activity_reporter", "reporters^uuid", "", null, 2, o, "POST");
}

function _activity_new ()
{
        var p = document.getElementById ("vp");
	var u = this.id.split ("-");
        var o = {};
	this.previousSibling.checked = true;
	argv (this.lastChild, o);
	if (o.case_id)
	{
        	elvpf = __(this,"vf").childNodes[1];
	}
	else
	{
		elvpf = __(this,"vb").nextSibling;
		jso (elvpf, o);
	}
	o["group"] = "reporter_contact_id";
        ra["dispositions_f"] = o;
        p.innerHTML = "";
	vp (p);
	nd (p, te[u[0]], [], [], [0]);
	p.firstChild.style.marginTop = window.scrollY+"px";
}

function _activity_show ()
{
	var coll = document.getElementById ("vv").childNodes;
	this.previousSibling.checked = true;
	coll[6].childNodes[1].firstChild.checked = true;
}

function _activity_vw_id (ev) 
{
	var coll = document.getElementById ("vv").childNodes;
	var a = {};
	var r_ = re["r_"][0].slice(0);
	var k = re["activities_k"];
	var u = ["activity_vw_id_tabs","activities"];
	var s_ = "";
	argv (this, a);
	var u_ = re["case_src"][a.src];
	if (/*a.src=="walkin") && */ a.src_uid==undefined) // simulate chani 
	{ 
		var user_cid = document.getElementById ("user_cid").value;
		a.src_ts = Date.now()/1000;
		a.src_uid = a.src+"-"+user_cid+"-"+Date.now ();
		if (a.src_callid==undefined) a.src_callid = a.src_uid;
		a.src_address =  "0700112233"; // debug
		a.src_usr = user_cid
		a.src_vector = 2;
		a.src_uid2 = a.src_uid+"-2";
		if (a.src_callid) 
		{
			s_ = "&src_vector="+a.src_vector+"&src_callid="+a.src_callid;
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
	if (re["case_src"][a.src][11]=="phone") r_[k["src_address"][0]] = _phone_fmt (a.src_address);
	u[0] = u_[9];
	if (a.src=="call")  u = ["activity_vw_id_tabs_call","activities^call"];

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
	nd (coll[6].childNodes[1].childNodes[1], te["activity_vw_id"], ["noop","1","",""], r_, [4]);	
	url (coll[6].childNodes[1].childNodes[1].lastChild, u[0], u[1], s);

	boo (ev)
}

