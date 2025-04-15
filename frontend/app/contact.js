
te["case_contact_ed_age"] = { c:
[
	{ div:["","vb"], c:[ { p:["","o"], c:
	[
		{ div:[], c:[ { input:["g","","age_t","0","radio","1"] }, { ac:["c w07 rc_","","_tab","x03 y","Age"] } ] },
		{ div:[], c:[ { input:["g","","age_t","1","radio"] }, { ac:["c w07 rc_","","_tab","xx y ","DOB"] } ] },
		{ div:[], c:[ { input:["g","","age_t","2","radio"] }, { ac:["d w07 rc_","","_tab","y tr","Age Group"] } ] }, 
		{ div:["e"] }
	]} ]},
	{ div:["","vaa"], c: 
	[
        	{ div:[], c:
        	[
        		{ input:["g","","age_vw","0","radio","1"] },
	        	{ p:["tabiv gws h03 b05","o"], c:[ { input:["w21 x tt b05 gws","","age",null,"",""], ev:["","_contact_age"] } ] },
	        ]},
	        { div:[], c:
	        [
		        { input:["g","","age_vw","2","radio"] },
			{ div:["tabiv"], c:
			[
				{ li:["w21 gws b05","va"], c:[ { div:[""], ev:["_dd"], c: 
				[					
					{ p:["c w17 x t03","o"], c:[ { p:["","calv"], ucalv:[" :d:dmy:0: ","dob",null] } ] }, 
					{ div:["d w02 x y content-hidden_"],  c:[ { div:["h02 w02 awb"] } ] },
					{ div:["d w02 x y content-shown_"],  c:[ { div:["h02 w02 awt"] } ] },
					{ div:["e"] }
				]} ]},
				{ div:["dd w21 sh xx b10 ba mtn1 gw_","vdd"], ev:["_undd"], c:
				[ 
					{ div:[], c:
					[
						{ ucal:["dob",null,"noop","1","", ""] },
						{ div:["e"] },
					]}
				]},
        	        	{ div:["","fn"], c:[ { div:["","_contact_dob"] } ] }
        		]}
        	]},
        	{ div:[], c:
		[
			{ input:["g","","age_vw","1","radio"] },
			{ div:["tabiv","tag-r_--o-case_age_tag_txa-%1-age_group_id-%0-noop"], c: 
        		[
        	        	{ li:["gws b05","va"], c:[ { div:["","category_ls-subcategories"], ev:["_dd"], c: // ls
        	        	[
        	        		{ p:["c w18","o"], c:
					[ 
						{ u:["case_age_tag_txa","r_"] }, 
						{ uchk:["tag",null,"","^","case_age_tag_txa",null,"age_group_id",null,"noop"] } 
					]},
					{ div:["d w02 x y"],  c:[ { div:["h02 w02 awb"] } ] },
					{ div:["e"], c:[ { arg:["_c","","10"] }, { arg:["root_id","",AGE_GROUP_ROOT_ID] } ] }
        	        	]} ]},
        	        	{ div:["dd w21 gw_ ba_b","vdd"], ev:["_undd"] },
        	        	{ div:[] },
        	        	{ div:["","fn"], c:[ { div:["","_contact_age_group"] } ] }
        		]},
        	]}	
        ]}
]};

te["case_contact_ed_r_"] = { c:  // 
[
	{ div:["tt"], c:
	[
		{ div:["c w41"], case_txt_:[null,"gww_ w41 x tt b05","fname",null,null] }, 
		{ div:["c w21 ll"], case_contact_ed_age:[null,null,null,null,null,null] },
		{ div:["e"] }
	]},
	{ div:["tt"], c:
	[
		{ div:["c w41"], case_loc_enum:["Location",null,null,null] },
		{ div:["c w21 ll"], case_sex_enum:["Sex",null,null,null] },
		{ div:["e"] }
	]},
	{ div:["tt"], c:
	[
		{ div:["c w41"], case_txt_:["Nearest Landmark","gww_ w41 x tt b05","landmark",null,"Enter Nearest Landmark"] },
		{ div:["c w21 ll"], case_nationality_enum:["Nationality",null,null,null] },		
		{ div:["e"] }
	]},
	
	{ div:["tt _clk_"], c:
	[
		{ div:["c w20"], case_national_id_type_enum:["ID Type",null,null,null] },
		{ div:["c w20 ll"], case_txt_:["ID Number","gww_ w20 x tt b05","national_id",null,"Enter Reporter's ID Number"] },
		{ div:["c w21 ll"], case_lang_enum:["Language",null,null,null] },
		{ div:["e"] }
	]},
	
	{ div:["tt"], c:
	[
		{ div:["c"], c:
		[
			{ s:["x y",null] },
			{ p:["","o"], c:
			[
				{ uchk:["case_yesno_r",null,"yesno","",  "is_refugee"," %2"] },
				{ div:["e"] }
			]}, 
		]},
		{ div:["d w21"], case_tribe_enum:["Tribe",null,null,null] },
		{ div:["e"] }
	]},
	
	{ div:["tt"], c:
	[
		{ div:["c w20"], case_txt_:["Phone Number","gws w20 x tt b05","phone",null,"Enter Reporter's Phone Number"] },
		{ div:["c w20 ll"], case_txt_:["Alternative Phone","gws w20 x tt b05","phone2",null,"Enter Alternate Phone Number"] },
		{ div:["c w21 ll"], case_txt_:["Email","gws w21 x tt b05","email",null,"Enter Reporter's Email Address"] },
		{ div:["e"] }
	]},
]};

te["case_contact_ed_"] = { div:["w68 ma sh__ gw_"], c:
[	
	{ div:["x15 tt"], c:
	[
		{ s:["c xx y12 n b",null] },
		{ ac:["d","","_uvp","xx y08 h cb","&Cross;"] },
		{ div:["e"] }
	]},

	{ div:["","ve"], c:
	[
		{ div:["x25 t"], c:[ { p:["c w55","nb"], u:["nb","contacts_nb"] }, { div:["e"] } ] },

		{ p:["x25","contact"], case_contact_ed_r_:
		[
"Name",":v:contacts:fullname","Enter Contact's Names",
":v:contacts:age",":v:contacts:dob",":v:contacts:dob",":v:contacts:age_group_id",":v:contacts:age_group"," %0", 
":v:contacts:location_id",":v:contacts:location"," %0",
":v:contacts:sex_id",":v:contacts:sex"," %0",  
":v:contacts:landmark",
":v:contacts:nationality_id",":v:contacts:nationality"," %0",
":v:contacts:national_id_type_id",":v:contacts:national_id_type"," %0",
":v:contacts:national_id", 
":v:contacts:lang_id",":v:contacts:lang"," %0", 
"Is a Refugee?",":v:contacts:is_refugee",
":v:contacts:tribe_id",":v:contacts:tribe"," %0",
":v:contacts:phone",
":v:contacts:phone2", 
":v:contacts:email"
		]},
		
                { p:["g","o"], arg:["","disposition_id",null] },		
				
		{ div:["w63 x25 t40 b20"], vp_sav:[null,null,null,null,null,null,null] }
	]}
]};

te["case_contact_ed"] = { case_contact_ed_:["Edit Contact",DISPOSITION_ID_CONTACT_EDIT, "case_contact_ed-contacts","_activity_postj","Update","Updating...","","_uvp", "Cancel"] };

te["case_contact_new"] = { case_contact_ed_:["New Contact", DISPOSITION_ID_CONTACT_NEW, "case_contact_new-contacts^disposition", "_activity_postj", "Create", "Creating...", "", "_uvp", "Cancel"] };

// ---

te["case_contact_vw_id_"] = { c:
[
	{ div:["tt"], c:
	[
		{ div:["c w41"], case_vw_val:["Fullname",null] },
		{ div:["c w21 ll"], c: 
		[
			{ s:["x tt v","Age"] },
			{ div:["x y02 n mh02"], c:
			[
				{ s:["c y03",null] }, // age
				{ div:["d x07 y03 bd gws"], uval:["",null] }, // age_group
				{ s:["d cd g",null] }, // dob
				{ div:["e"] }
			]}
		]},
		{ div:["e"] }
	]},
	{ div:["tt"], c:
	[
		{ div:["c w41 t03"], c:
		[
			{ div:["x y n mh02 bd"], uval:["location",null] }
		]},
		{ div:["c w21 ll"], case_vw_val_cat:["Sex","",null] },
		{ div:["e"] }
	]},
	{ div:["tt"], c:
	[
		{ div:["c w41"], case_vw_val:["Nearest Landmark",null] },
		{ div:["c w21 ll"], case_vw_val_cat:["Nationality","",null] },
		{ div:["e"] }
	]},
	{ div:["tt _clk_"], c:
	[
		{ div:["c w20"], case_vw_val_cat:["ID Type","",null] },
		{ div:["c w20 ll"], case_vw_val:["ID Number",null] },
		{ div:["c w21 ll"], case_vw_val_cat:["Language","",null] },
		{ div:["e"] }
	]},
	{ div:["tt"], c:
	[
		{ div:["c w20"], case_vw_val:["Is a Refugee",null] },
		{ div:["d w21"], case_vw_val_cat:["Tribe","",null] },
		{ div:["e"] }
	]},
	{ div:["tt"], c:
	[
		{ div:["c w20"], case_vw_val:["Phone Number",null] },
		{ div:["c w20 ll"], case_vw_val:["Alternative Contact",null] },
		{ div:["c w21 ll"], case_vw_val:["Email",null] },
		{ div:["e"] }
	]}, 
	
]};

// ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

te["contact_ed_r_"] = { div:["","ve"], c:
[
	{ div:["x"], c:[ { p:["c w40","nb"], u:["nb","contacts_nb"] }, { div:["e"] } ] },
	{ p:["","o"], c:
	[
		{ div:["t15"], c:
		[
			{ s:["c w13 y","First Name"] }, { txt:["c w25 gw ba","w25 x y","","fname","%8"] }, { div:["e"] }
		]},
		{ div:["t15"], c:
		[
			{ s:["c w13 y","Last Name"] }, { txt:["c w25 gw ba","w25 x y","","lname","%9"] }, { div:["e"] }
		]},
		{ div:["t15"], c:
		[
			{ s:["c w13 y","Phone"] }, { txt:["c w25 gw ba","w25 x y","","phone","%10"] }, { div:["e"] }
		]},
		{ div:["t15"], c:
		[
			{ s:["c w13 y","Email"] }, { txt:["c w25 gw ba","w25 x y","","email","%11"] }, { div:["e"] }
		]},
		{ div:["t15"], c:
		[
			{ s:["c w13 y","Membership"] }, { txt:["c w25 gw ba","w25 x y","","membership","%13"] }, { div:["e"] }
		]},
		{ div:["t15"], c:
		[
			{ s:["c w13 y","DNC Status"] }, { txt:["c w25 gw ba","w25 x y","","dnc","%13"] }, { div:["e"] }
		]},
		
	]},
	{ div:["t35"], c:
	[
		{ div:["c w06 r02"], c:[ { ac:["aa btn",null,"_postj","x y04 w05 gbl cw tc","Save"] }, { s:["y07 bd b savl","..."] } ] },
		{ div:["c l20","va"], ac:["ay",null,null,"x y04 w05 gwd tc cbr","Cancel"], c:[ { p:["g","o"], arg:["",".id","%0"] } ] },
		{ div:["e"] }
	]}
]};

te["contact_ed_r"] = { contact_ed_r_:["contact_ed-contacts","contact_vw_id-contacts-vp","_u"] };

te["contact_new_r"] = { contact_ed_r_:["contact_new-contacts","","_vpclose"] };

te["contact_ed"] = { vped:["w60 ma bd sh__ gw","Edit Contact","contact_ed_r"] };

te["contact_new"] = { vped:["w60 ma bd sh__ gw","New Contact","contact_new_r"] };

// ------------------------------------------

te["contact_vw_rv_phone"] = { c:
[
	{ div:["x s"], c:
	[
		{ s:["c l x y micon","call"] },
		{ div:["c y"], uval:["",null] },
		{ s:["c l20 y micon","email"] },
		{ div:["c y"], uval:["",null] },
		{ div:["e"] }
	]}
]};

te["contact_vw_rv"] = { c:
[
	{ div:["x t"], c:
	[
		{ div:["c l t"], uval:["",null] },
		{ s:["c t",","] },
		{ div:["c ll t"], uval:["",null] },
		{ s:["c t",","] },
		{ div:["c ll t"], uval:["",null] },
		{ div:["e"] }
	]},
	{ div:["x s"], c:
	[
		{ div:[" x t"], uval:["",null] },
		{ s:["c x t s cd","Nearest Landmark:"] },
		{ s:["c t i",null] },
		{ div:["e"] }
	]},
]};

te["contact_vw_r"] = { div:[""], c:
[
	{ div:["x15 b10"], case_contact_vw_id_:
	[
":v:contacts:fullname",":v:contacts:age",":v:contacts:age_group",":v:contacts:dob",
":v:contacts:location",":v:contacts:sex",
":v:contacts:landmark",":v:contacts:nationality",
":v:contacts:national_id_type",":v:contacts:national_id", ":v:contacts:lang",
":v:contacts:is_refugee::yesno:2", ":v:contacts:tribe",
":v:contacts:phone",":v:contacts:phone2",":v:contacts:email"
	]}
]};

te["contact_vw_id"] = { div:["w66 ma bd sh__ y gw_","vddvw"], ev:["_undd"], c:
[
	{ div:["x15 tt"], c:
	[
		{ s:["c x yy h3 b","Contact Details"] },
		{ ac:["d ay","","_uvp","x bd cb",""], c:[ { s:["c h y03","&Cross;"] }, { s:["c x y g","Close"] }, { div:["e"] } ] },
		// todo: block|unblock 
		// { div:["d xx ay","va"], ac:["r05","contact_ed-contacts-vp","_u","xx y gww cb bd","Edit"], c:[ { arg:["",".id","%0"] } ] },
		{ div:["e"] }
	]},
	{ contact_vw_r:[] }
]};

// ----------------------------------------

te["contact_lc_menu"] = { div:["c lcfmenu"], c:
[
	{ ac:["c w02_ aa","contact_new-r_","_vp","b h2 y03 tc cb","&plus;"] },
	{ ac:["c w02_ aa","","","b h2 y03 tc cb","&equiv;"] },
]};

te["contact_lc_r"] = { div:[], c:
[
	{ input:["g","","contact_id","","checkbox"] },
	{ li:["c w01_ x y08 r"],  ev:["_chk_tag"], s:["chk",""], c:
	[
		{ arg:["id-0","","%0"] }, { arg:["fullname-7","","%7"] }, { arg:["phone-10","","%10"] }
	]},
	{ input:["g","","vpf","","radio"] },
	{ li:["c w25 x r","contact_vw_id-contacts-"], ev:["_vp"], s:["",""], c:
	[
		{ div:["c w17"], s:[" tt h02","%7"] },
		{ div:["d w08"], s:[" tt h02 tr","%10"] },
		{ div:["e"], arg:["",".id","%0"] }
	]},
	{ div:["e"] }
]};

te["contact_lc_pg"] = { pg:["pgto","contact_lc-contacts"," dh","da dl","contact_lc-contacts"," dh","da dr"] };

te["contact_lc"] = { lst:["noop","noop","noop","noop","noop",  "h30 x07 y","contact_lc_r","contacts", "x07 y07","contact_lc_menu","d","contact_lc_pg"] };

// -------------------------------------

te["contact_ls_footer"] = { div:["x gws"], c:
[
	{ s:["c x y cd s","%3"] },
	{ s:["c y cd s","of"] }, 
	{ s:["c x y cd s","%4"] },
	{ div:["d t03"], c:[ { ac:["nav","contact_ls-contacts","_nav","dh",""], c:[ { div:["da dr_"] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] },
	{ div:["d t03"], c:[ { aci:["nav","contact_ls-contacts","_nav","dh","prev",""], c:[ { div:["da dl_"] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] },
	{ div:["e"] }
]};

te["contact_ls_r"] = { div:[], c:
[
	{ ac:["ay","case_contact_ed-contacts-ve-contact","_sel","x t07 b05 cb  bb_",""], c:
	[
		{ div:["s"], c:
		[
			{ s:["c w16 x n","%8"] },
			{ s:["d x","%19"] },
			{ s:["d x","%17"] },
			{ div:["e"] }
		]},
		{ div:["s"], c:
		[
			{ s:[" x t","%11"] },
			{ s:[" x t","%24"] },
			{ div:["e"] }
		]},
		{ div:["e"], c:[ { arg:["id-0","","%0"] }, { arg:["fullname-8","","%8"] } ] } // no need for other field coz selu will populate fields
	]},
	{ div:[], arg:[".id","","%0"] }
]};

te["contact_ls"] = { list:["end","end","","noop","contact_ls_r","contacts", "contact_ls_footer"] };

// ---------------------------

te["contact_f_tags_"] = { c: 
[

	{ f:["Name",null,	" %0","fullname",""] },
	{ f:["Phone",null,	" %0","phone",""] },
	{ f:["Age",null,	" %1","age_group_id"," %1"] },
	{ f:["Gender",null,	" %1","sex_id"," %1"] },
	{ f:["Location",null,	" %1","location_id"," %1"] },
	{ f:["ID Type",null,	" %1","national_id_type_id"," %1"] },
	{ f:["Nationality",null," %1","nationality_id"," %1"] },
	{ f:["Language",null,	" %1","lang_id"," %1"] },
	{ f:["Tribe",null,	" %1","tribe_id"," %1"] },

	{ f:["Created By",null,		" %1","created_by_id"," %1"] },
	{ f:["Created On",null,		" :d:dmy:0: ","created_on",""] },
	{ div:["e"] }
]};

te["contact_f_tags_k"] = { contact_f_tags_:
[
":k:contacts_k:fullname:2", 
":k:contacts_k:phone:2", 
":k:contacts_k:age_group_id:2", 
":k:contacts_k:sex_id:2", 
":k:contacts_k:location_id:2", 
":k:contacts_k:national_id_type_id:2",
":k:contacts_k:nationality_id:2",
":k:contacts_k:lang_id:2",
":k:contacts_k:tribe_id:2",
":k:contacts_k:created_by_id:2", 
":k:contacts_k:created_on:2"
]};

te["contact_f_tags"] = { contact_f_tags_:
[
":k:contacts_f:fullname", 
":k:contacts_f:phone", 
":k:contacts_f:age_group_id", 
":k:contacts_f:sex_id", 
":k:contacts_f:location_id", 
":k:contacts_f:national_id_type_id",
":k:contacts_f:nationality_id",
":k:contacts_f:lang_id",
":k:contacts_f:tribe_id",
":k:contacts_f:created_by_id", 
":k:contacts_f:created_on"
]};

te["contact_f"] = { div:["w55 ma sh__ y gw_","vddvf"], ev:["_undd"], c: 
[
	{ s:["x20 yy b","Search Contact"] },
	{ div:["l15 r30 tt b20"], c:
	[
		{ div:["xx yy"], kf_s:["Name","fullname",":k:contacts_f:fullname"] },
	{ div:["xx yy"], kf_s:["Phone","phone",":k:contacts_f:phone"] },
	{ div:["xx yy"], kf_l:["Age","tag_-r_--o--%1-category_id-age_group_id-%0-%1", "case_lc_main-subcategories", 
":k:contacts_f:age_group_id", ""," %1","category_id","age_group_id"," %0"," %1", "case_age_group_root_id"] },
	{ div:["xx yy"], kf_l:["Sex","tag_-r_--o--%1-category_id-sex_id-%0-%1", "case_lc_main-subcategories",  
":k:contacts_f:sex_id", ""," %1","category_id","sex_id"," %0"," %1", "case_sex_root_id"] },
	{ div:["xx yy"], kf_l:["Location","tag_-r_--o--%1-category_id-location_id-%0-%1", "case_location_lc_main-subcategories",  ":k:contacts_f:location_id", ""," %1","category_id","location_id"," %0"," %1", "case_location_root_id"] },

	{ div:["xx yy"], kf_l:["ID Type","tag_-r_--o--%1-category_id-national_id_type_id-%0-%1", "case_lc_main-subcategories",  ":k:contacts_f:national_id_type_id", ""," %1","category_id","national_id_type_id"," %0"," %1", "case_national_id_type_root_id"] },

	{ div:["xx yy"], kf_l:["Nationality","tag_-r_--o--%1-category_id-nationality_id-%0-%1", "case_lc_main-subcategories",  ":k:contacts_f:nationality_id", ""," %1","category_id","nationality_id"," %0"," %1", "case_nationality_root_id"] },

	{ div:["xx yy"], kf_l:["Language","tag_-r_--o--%1-category_id-lang_id-%0-%1", "case_lc_main-subcategories",  ":k:contacts_f:lang_id", ""," %1","category_id","lang_id"," %0"," %1", "case_lang_root_id"] },

	{ div:["xx yy"], kf_l:["Tribe","tag_-r_--o--%1-category_id-tribe_id-%0-%1", "case_lc_main-subcategories",  ":k:contacts_f:tribe_id", ""," %1","category_id","tribe_id"," %0"," %1", "case_tribe_root_id"] }

	// todo: createdon,createdby, status

	]},
	{ vp_apply:["contact_f_tags-contacts_f"] }
]};

// ---------------------------------------------

te["contact_footer"] = { div:["x ba"], c:
[
	{ div:["d y07"], pg:["pgto","contact_list-contacts"," dh","da dl","contact_list-contacts"," dh","da dr"] },
	{ div:["e"] }
]};

te["contact_r"] = { li:["w160 gw","contact_vw_id-contacts"], ev:["_vp"], c:
[
	{ div:["c w20 tt b05 h01_"], s:["xx",":v:contacts:fullname"] },
	{ div:["c w10 tt b05 h01_"], s:["xx",":v:contacts:sex"] }, 
	{ div:["c w10 tt b05 h01_"], s:["xx",":v:contacts:age_group"] }, 
	{ div:["c w15 tt b05 h01_"], s:["xx",":v:contacts:phone"] },
        { div:["c w40 tt b05 h01_"], s:["xx",":v:contacts:location"] },
	{ div:["c w15 tt b05 h01_"], s:["xx",":v:contacts:created_by"] },
	{ div:["c w15 tt b05 h01_"], s:["xx",":d:dmyhn:1: "] },
	{ div:["e"], arg:["",".id","%0"] } 
]};

te["contact_k"] = { div:["w160 bt bb gw"], s:["",""], c:
[
	{ k_a:["c w20","","cd","Full Name","da db","fname",":k:contacts_k:fullname:2"] },
	{ k_a:["c w10","","cd","Gender","da db","sex_id",":k:contacts_k:sex_id:2"] },
	{ k_a:["c w10","","cd","Age Group","da db","age_group_id",":k:contacts_k:age_group_id:2"] },
	{ k_a:["c w15","","cd","Phone","da db","phone",":k:contacts_k:phone:2"] },
	{ k_a:["c w40","","cd","Location","da db","location_id",":k:contacts_k:location_id:2"] },
	// { k_a:["c w20","","cd","Email","da db","email",":k:contacts_k:email:2"] },
	{ k_a:["c w15","","cd","Created By","da db","created_by",":k:contacts_k:created_by:2"] },
	{ k_a:["c w15","","cd","Created On","da db","created_on",":k:contacts_k:created_on:2"] },
	{ k_a:["c w15","","cd","Status","da db","status",":k:contacts_k:status:2"] },

	{ arg:["","cases^id",":k:contacts_k:cases^id:2"] },
	{ arg:["","cases^created_on",":k:contacts_k:cases^created_on:2"] },
	{ arg:["","cases^created_by_id",":k:contacts_k:cases^created_by_id:2"] },
	{ arg:["","cases^src",":k:contacts_k:cases^src:2"] },
	{ arg:["","cases^case_category_id",":k:contacts_k:cases^case_category_id:2"] },
        { arg:["","cases^gbv_related",":k:contacts_k:cases^gbv_related:2"] },
	{ arg:["","cases^priority",":k:contacts_k:cases^priority:2"] },
	{ arg:["","cases^status",":k:contacts_k:cases^status:2"] },
	{ arg:["","cases^escalated_to_id",":k:contacts_k:cases^escalated_to_id:2"] },
	{ arg:["","cases^assessment_id",":k:contacts_k:cases^assessment_id:2"] },
	{ arg:["","cases^justice_id",":k:contacts_k:cases^justice_id:2"] },
	
	{ div:["e"] }
]};

te["contact_nb"] = { div:[], c:[ { u:["nb","contacts_nb"] }, { div:["e"] } ] };

te["contact_title"] = { div:[] }; 

te["contact_list"] = { list:["contact_title","contact_nb","bl br ox","contact_k","contact_r","contacts","contact_footer"] };

te["contact_main"] = { c:
[
	{ div:["tt","vb"], c:
	[
		{ div:["c t03"], c:
		[
			{ div:["","va"], s:["",""], c:
			[
				{ input:["g","","contact_t_","0","radio","1"] },
				{ ac:["c","contact_main-contacts-vftab","_u","x y cb b h2","Contacts"] }, 
				//{ ac:["c t02 x ay","","_dd","h02 w02 gws_ awb",""] },
				{ div:["e"] } //, arg:["","_title","%5"] }
			]},
			{ div:["dd x y gw ba sh nd w14","vdd"], c:
			[
			
			]}
		]},
		
		// { div:["c l40"], c: 
		//[
		//	{ arg:["contact_list-contacts","","0"] },
		//	{ input:["g","","contacts_t_","0","radio","1"] },
		//	{ li:["opto x bl bt bb gw s cb","contact_list-contacts"], ev:["_tab"], c:
		//	[
		//		{ s:["c l t h3_ micon","list"] },
		//		{ div:["c xx y","","List"] }, 
		//		{ div:["e"] }
		//	]}
		//]},

		//{ div:["c"], c: 
		//[
		//	{ arg:["contact_rpt_vw-contacts-@","","1,0"] },
		//	{ input:["g","","contacts_t_","1","radio"] },
		//	{ li:["opto x ba gw s cb","contact_rpt_main-r_"], ev:["_tab"], c:[ { div:[], c:
		//	[
		//		{ s:["c l t h3_ micon","bar_chart"] },
		//		{ s:["c xx y","Reports"] }, 
		//		{ div:["e"] }
		//	]} ]}
		//]}, 

		{ div:["c l40"], ac:["ay","contact_f-contacts_f","_vpf","x t01 bd_ cb s",""], c:
		[ 
			{ s:["c t04 h3_ micon","search"] },
			{ div:["c x y","","Search"] }, 
			{ div:["e"] }
		]},

		// { div:["c l40"], ac:["ay","contacts","_download","x t01 bd_ cb s",""], c:
		//[ 
		//	{ s:["c t04 h3_ micon","download"] },
		//	{ div:["c x y","","Download"] }, 
		//	{ div:["e"] }
		//]},
		
		{ div:["e"], c:[ { arg:["","","contact_list-contacts"] }, { arg:["","","0"] }, { arg:["","","-1"] }, { arg:["","",""] } ] }
	]},

	{ div:["yy","vf"], c:[ { div:["","contact_f-contacts_f"], c: // ev:["_n_vpf"], c:
	[
		{ contact_f_tags_k:[] }
	]} ]},

	{ div:[], c:
	[
		{ div:[], c:[ { input:["g","","contacts_v","0","radio","1"] }, { p:["tabv yy","vt"], contact_list:[] } ] },
		{ div:[], c:[ { input:["g","","contacts_v","1","radio"] }, { p:["tabv","vt"] } ] },				
	]}
]};
	
te["contacts"] = { c:
[
	{ div:["g"], c:
	[
		
	]},
	{ form:[], c:
	[
		{ div:[], c:
		[	
			{ input:["g","","contact_vw_vt","0","radio","1"] }, 
			{ p:["tabv x20 y20 gw mm","vftab"], contact_main:[] } 
		]},
		{ div:[], c:
		[	
			{ input:["g","","contact_vw_vt","1","radio"] }, 
			{ p:["tabv gw yy mm","vfvw"] }
		]}
	]}
]};


function contact_dob (p, v)
{
	var today = new Date ();
	var year = today.getFullYear ();
	var month = today.getMonth();
	var day = today.getDate();
	var dob = new Date (year-v, month, day);
	var el = _(p.childNodes[1].childNodes[1].firstChild,"calv");
	el.innerHTML = "";
	if (v==="") return;
	nd (el, te["tag_calv"], ["%0", "dob",":d:dmy:0: "], [(""+(Math.floor(dob.getTime() / 1000)))], [3]);
}

function contact_age_group (p, v)
{
	var el = _(p.childNodes[2].childNodes[1].firstChild,"o");
	var aa = re["categories_age_group"];
	var m = [-1,-1]
	
	el.innerHTML = "";
	if (v==="") return;

	for (var i=0; i<aa.length; i++)
	{
		var vv = aa[i][5].split ("-");
		if (!Number.isInteger (vv[0]*1)) 
		{
			vv = aa[i][5].split (" ");
			console.log ("[agegroup]"+vv[0]+","+vv[1]+",")
			if (vv[0]=="Above" && (vv[1]*1)<=(v*1))
			{
				m[0]=i;
			}
			continue;
		}
		if (vv.length>1 && Number.isInteger (vv[1]*1)) // cmp in range
		{
			if ((vv[0]*1)<=v && (vv[1]*1)>=v) m[0]=i	
			continue;
		}
		if ((vv[0]*1)<=v) m[1]=i;
	}
	
	//console.log ("AGEGROUP: '"+v+"' ["+m[0]+","+m[1]+"]")
		
	i=-1;
	if (m[1]>-1) i=m[1]
	if (m[0]>-1) i=m[0]
	if (i<0) return;
		
	nd (el, te["tag"], ["noop","%0","age_group_id","%6","case_age_tag_txa"], aa[i], [5]);
}

function contact_age (p, v)
{
	var el = p.firstChild.childNodes[1].firstChild;
	el.value = v;
}

function _contact_dob (el, r)
{
	var today = new Date ();
	var dob = new Date (r[0]*1000);
	var age = Math.floor ((today.getTime()-dob)/31536000000);
	//console.log ("age: "+age);
	contact_age (__(el,"vaa"), age);
	contact_age_group (__(el,"vaa"), age); 
}

function _contact_age_group (el, r)
{
	var p = __(el,"vaa")
	var vv = r[1].split ("^")[1].split("-");
	var age = vv[0];
	if (!Number.isInteger (vv[0]*1)) age="";
	if (vv.length>1 && Number.isInteger (vv[0]*1) && Number.isInteger (vv[1]*1)) age = Math.floor ((vv[0]*1) + ((vv[1]-vv[0])/2));
	//console.log ("AGE: '"+age+"' | "+vv[0]+"-"+vv[1])
	contact_age (p, age);
	contact_dob (p, age); 
}

function _contact_age ()
{
	var p = __(this,"vaa")
	var age = this.value*1;
	contact_dob (p, age); 
	contact_age_group (p, age);
}

