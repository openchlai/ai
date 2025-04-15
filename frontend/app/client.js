
te["case_client_del"] = { c:
[
	{ div:["l cr gp"], c:
	[
		{ s:["c x y","Client Deleted"] },
		{ ac:["d ay ga","","_rm","x y h2","&Cross;"] },
		{ div:["e"] }
	]},
	{ ufn:["case_client_del_ufn"] }
]};

te["case_form_client_r_"] = { c:
[
	{ div:["","ve"], c:
	[
		{ input:["g","","case_form_a","%0","radio"] },
		{ li:["x y bd cb gbn","client_ed-clients-^"], ev:["_vp"], c:
		[
			{ div:[], c:
			[
				{ div:["d w03"], ac:["abs w03","client_del-clients^del","_del","cb h2",""], c:
				[
					{ s:["x y h2 tc","&Cross;"] },
					{ div:[], c:[ { arg:["",".id","%0"] } ] }
				]},
				{ div:["e"] }
			]},
			{ contact_vw_rv:[":v:clients:contact_fullname", ":v:clients:contact_age_group", ":v:clients:contact_sex", ":v:clients:contact_location", ":v:clients:contact_landmark"] },
			{ contact_vw_rv_phone:[":v:clients:contact_phone", ":v:clients:contact_email"] },
			{ div:["g"], arg:["",".id","%0"] }
		]},
		{ div:["g"], arg:["","","case_form_client_r_-clients-va--@"] },
	]},
	{ div:[], arg:["o","client_id","%0"] }
]};

te["case_form_client_r"] = { div:["mb","va"], case_form_client_r_:[] };

// --------

te["case_client_marital_sel_sub"] = { div:["","sub"], c:
[
	{ arg:["case_client_ed_sub_spouse,case_client_ed_sub_spouse,case_client_ed_sub_spouse,case_client_ed_sub_spouse,case_client_ed_sub_spouse-r_-ve-_case_client_spouse_","", MARITAL_STATUS_WITH_SPOUSE_ID] },
]};

te["case_client_marital_tag_txa"] = { case_enum_tag_txa_:["w21 xx tt b05","fullname__","Select Marital Status","marital_id"] };

te["case_client_marital_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_client_marital_tag_txa-%1-marital_id-%0-%2", "category_ls-subcategories", "c w17", 
"case_client_marital_tag_txa","r_", 
null, "case_client_marital_tag_txa",null,"marital_id",null," %2", 
MARITAL_STATUS_ROOT_ID, "fullname", "noop", 
"dd w21 gw_ ba_b", 
"case_client_marital_sel_sub"] };

// ----

te["case_client_ed_sub_disabled_services"] = {  c:
[
	{ div:["yy"], case_enum_lc:["x y","Special Services Referal","",  
"taga-r_--a--%1-category_id-%0-%2", "case_lc_main-subcategories", "client_referals", "c w39",    
":v:clients:is_disabled_referals","client_referal_del-client_referals-client_id"," %1","category_id"," %0","%2",  
CASE_REFERALS_ROOT_ID,"noop", 
"dd w42 ba_b gw_","noop"] }
]};

te["case_client_ed_sub_disabled"] = { div:["b20"], c:
[	
	{ div:["c w20"], case_disability_enum:["Disability",":v:clients:disability_id",":v:clients:disability"," %0"] },
	{ div:["c w42 ll","va"], c: // case_txt_:["Is the Client refered for Special Services?","gws w42 x tt b05","special_services",":v:clients:special_services",""] },
	[
		{ s:["x y","Is the Client refered for Special Services?"] },
		{ p:["t03","o"], c:
		[
			{ uchk:["case_yesno_r",":v:clients:is_disabled_refered","yesno","",  "is_disabled_refered"," %2"] },
			{ div:["e","sub"], arg:["case_client_ed_sub_disabled_services-r_-ve-_case_client_disabled_services_","","1"] }		
		]},
		{ p:["","_case_client_disabled_services_"], usub:["case_client_ed_sub_disabled_services","r_",":v:clients:is_disabled_refered","1"] }
	]},
	{ div:["e"] }
]};

te["case_client_ed_sub_inschool_yes"] = { div:["b20"], c:
[
	{ div:["t15"], c:
	[	
		{ div:["c w41"], case_txt_:["School Name","gws w41 x tt b05","school_name",":v:clients:school_name",""] },
		{ div:["c w21 ll"], case_school_level_enum:["School Level",":v:clients:school_level_id",":v:clients:school_level"," %0"] },
		{ div:["e"] }
	]},
	{ div:["tt"], c:
	[	
		{ div:["c w41"], case_txt_:["School Address","gws w41 x tt b05","school_address",":v:clients:school_address",""] },
		{ div:["c w21 ll"], case_school_type_enum:["School Type",":v:clients:school_type_id",":v:clients:school_type"," %0"] },
		{ div:["e"] }
	]},
	{ div:["yy"], c:
	[	
		{ div:["c w41"], case_txt_:["School Attendance","gws w41 x tt b05","school_attendance",":v:clients:school_attendance",""] },
		{ div:["e"] }
	]},
]};

te["case_client_ed_sub_inschool_no"] = { div:["b20"], c:
[	
	{ div:["w62 t15"], case_txt_:["Reason for not attending school","gws w62 x tt b05","not_in_school_reason",":v:clients:not_in_school_reason",""] },
]};

te["case_client_ed_sub_spouse"] = { div:["t15 b20"], c:
[	
	{ div:["c w41"], case_txt_:["Client's Spouse Name","gws w41 x tt b05","spouse_fullname",":v:clients:spouse_fullname",""] },
	{ div:["c w21 ll"], case_spouse_employment_enum:["Client's Spouse Profession",":v:clients:spouse_profession_id",":v:clients:spouse_profession"," %0"] },
	{ div:["e"] }
]};

// ---

te["case_client_ed_"] = { div:["w68 ma mb sh__ gw_"], c:
[
	{ div:["x15 tt"], c:
	[
		{ s:["c xx y12 n b",null] },
		{ ac:["d","","_uvp","xx y08 h cb","&Cross;"] },
		{ div:["e"] }
	]},
			
	{ div:["","ve"], c:
	[
		{ div:["x25 t"], c:[ { p:["c w55","nb"], u:["nb","clients_nb"] }, { div:["e"] } ] },

		{ p:["x25 clk_client","contact"], case_contact_ed_r_:
		[
"Client's Name",":v:clients:contact_fullname","Enter Client's Names",
":v:clients:contact_age",":v:clients:contact_dob",":v:clients:contact_dob",":v:clients:contact_age_group_id",":v:clients:contact_age_group"," %0", 
":v:clients:contact_location_id",":v:clients:contact_location"," %0",
":v:clients:contact_sex_id",":v:clients:contact_sex"," %0",  
":v:clients:contact_landmark",
":v:clients:contact_nationality_id",":v:clients:contact_nationality"," %0",
":v:clients:contact_national_id_type_id",":v:clients:contact_national_id_type"," %0",
":v:clients:contact_national_id", 
":v:clients:contact_lang_id",":v:clients:contact_lang"," %0", 
"Is the Client a Refugee?",":v:clients:contact_is_refugee",
":v:clients:contact_tribe_id",":v:clients:contact_tribe"," %0",
":v:clients:contact_phone",
":v:clients:contact_phone2", 
":v:clients:contact_email", 
		]},	
		
		{ div:["x25 t15"], c:
                [
                        { div:["c w20"], case_rela_enum:["Reporter's Relationship with Client",":v:clients:relationship_id",":v:clients:relationship"," %0"] },
                        { div:["c w42 ll"], case_txt_:["Relationship <br/>Comment","gws w42 x yy","relationship_comment",":v:clients:relationship_comment","Enter Comments about the relationship"] },
                        { div:["e"] }
                ]},

		{ div:["x25 tt"], c:
		[
			{ div:["c w20"], case_txt_:["Number of Adult<br/> in Household","gws w20 x tt b05","household_adults",":v:clients:household_adults",""] },			
			{ div:["c w20 ll"], case_household_enum:["Household <br/> Type",":v:clients:household_id",":v:clients:household"," %0"] },
			{ div:["c w21 ll"], case_household_head_employment_enum:["Head of Household<br/> Occupation", ":v:clients:household_head_occupation_id",":v:clients:household_head_occupation"," %0"] },
			{ div:["e"] }
		]},

		{ div:["x25 t15"], c:
		[
			{ div:["c w41"], case_txt_:["Parent/Guardian's Name","gws w41 x tt b05","guardian_fullname",":v:clients:guardian_fullname",""] },
			{ div:["c w21 ll"], case_guardian_marital_enum:["Parent/Guardian's Marital Status",":v:clients:guardian_marital_id",":v:clients:guardian_marital"," %0"] },
			{ div:["e"] }
		]},

		{ div:["x25 tt"], c:
		[
			{ div:["c w20"], case_txt_:["Parent/Guardian's Identification Number","gws w20 x tt b05", "guardian_national_id", ":v:clients:guardian_national_id", ""] },
			{ div:["e"] }
		]},
		
		{ div:["x25 t15 "], c:
		[	
			{ div:["c w20"], case_health_enum:["Client's Health Status",":v:clients:health_id",":v:clients:health"," %0"] },
			{ div:["c w20 ll"], case_hiv_enum:["Client's HIV Status",":v:clients:hiv_id",":v:clients:hiv"," %0"] },
			{ div:["c w21 ll"], case_client_marital_enum:["Clients's Marital Status",":v:clients:marital_id",":v:clients:marital"," %0"] },
			{ div:["e"] }
		]},
		
		{ p:["x25","_case_client_spouse_"], usub:["case_client_ed_sub_spouse,case_client_ed_sub_spouse,case_client_ed_sub_spouse,case_client_ed_sub_spouse,case_client_ed_sub_spouse", "r_", ":v:clients:marital_id", MARITAL_STATUS_WITH_SPOUSE_ID] },


		{ div:["x25 t15","va"], c:
		[
			{ s:["x t","Is the Client Attending School?"] },
			{ p:["","o"], c:
			[
				{ uchk:["case_yesno_r",":v:clients:in_school","yesno","",  "in_school"," %2"] },
				{ div:["e","sub"], arg:["case_client_ed_sub_inschool_no,case_client_ed_sub_inschool_yes-r_-ve-_case_client_inschool_","","0,1"] }
			]},
		]},

		{ p:["x25","_case_client_inschool_"], usub:["case_client_ed_sub_inschool_no,case_client_ed_sub_inschool_yes","r_",":v:clients:in_school","0,1"] },
		
		{ div:["x25 t15","va"], c:
		[
			{ s:["x t","Is the Client Disabled?"] },
			{ p:["","o"], c:
			[
				{ uchk:["case_yesno_r",":v:clients:is_disabled","yesno","",  "is_disabled", " %2"] },
				{ div:["e","sub"], arg:["case_client_ed_sub_disabled-r_-ve-_case_client_disabled_","","1"] }
			]}
		]},

		{ p:["x25","_case_client_disabled_"], usub:["case_client_ed_sub_disabled","r_",":v:clients:is_disabled","1"] },

		{ div:["x25 t30 b20"], vp_sav:[null,null,null,null,null,null,null] }
	]}
]};	

te["case_client_ed"] = { case_client_ed_:["Edit Client Details","client_ed-clients","_activity_case_postj","Update","Updating...","client_vw_id-clients-vp","_u","Cancel"] };

te["case_client_new"] = { case_client_ed_:["New Client","client_new-clients","_activity_case_postj","Create","Creating...","","_uvp","Cancel"] };

// --------------------------------------------------------------------------------------------

te["case_vw_client_r_"] = { div:["","ve"], c: 
[
	{ input:["g","","case_vw_a","%0","radio",""] },
	{ li:["xx y bd cb gws_","client_vw_id-clients-^"], ev:["_vp"], s:["",""], c:
	[
		{ contact_vw_rv:[":v:clients:contact_fullname", ":v:clients:contact_age_group", ":v:clients:contact_sex", ":v:clients:contact_location", ":v:clients:contact_landmark"] },
		{ contact_vw_rv_phone:[":v:clients:contact_phone", ":v:clients:contact_email"] },
		{ div:["g"], arg:["",".id","%0"] }
	]},
	{ div:["g"], arg:["","","case_vw_client_r_-clients-va--@"] },
]};

te["case_vw_client_r"] = { div:["mb","va"], case_vw_client_r_:[] };

// -----------------------------

te["case_client_vw_disabiliy_services"] = { div:[""], c:
[
	{ s:["x tt cd","Referals"] },
	{ div:["r05 b05 n"], c:
	[ 
		{ uchk:["tagv",":v:clients:is_disabled_referals","","",  "x y bd gws"," %1"] }, 
		{ div:["e"] }
	]},
]};

te["case_client_vw_sub_disabled"] = { div:["x15 yy"], c:
[	
	{ div:["c w20"], case_vw_val:["Disability",":v:clients:disability"] },
	{ div:["c w42 ll","va"], c: 
	[
		{ case_vw_val:["Is the Client Refered for Special Services?",":v:clients:is_disabled_refered::yesno:2"] },
		{ div:[], usub:["case_client_vw_disabiliy_services","r_",":v:clients:is_disabled_refered","1"] }
	]},
	{ div:["e"] }
]};

te["case_client_vw_sub_inschool_yes"] = { div:["x15"], c:
[
	{ div:["tt"], c:
	[	
		{ div:["c w41"], case_vw_val:["School Name",":v:clients:school_name"] },
		{ div:["c w21 ll"], case_vw_val_cat:["School Level","",":v:clients:school_level"] },
		{ div:["e"] }
	]},
	{ div:["tt"], c:
	[	
		{ div:["c w41"], case_vw_val:["School Address",":v:clients:school_address"] },
		{ div:["c w21 ll"], case_vw_val_cat:["School Type","",":v:clients:school_type"] },
		{ div:["e"] }
	]},
	{ div:["yy"], c:
	[	
		{ div:["c w41"], case_vw_val:["School Attendance",":v:clients:school_attendance"] },
                { div:["c w21 ll"], case_vw_val_cat:["School Type","",":v:clients:school_type"] },
		{ div:["e"] }
	]},
]};

te["case_client_vw_sub_inschool_no"] = { div:["x15 yy"], c:
[	
	{ div:["w62"], case_vw_val:["Reason for not attending school",":v:clients:not_in_school_reason"] }
]};

te["case_client_vw_sub_spouse"] = { div:["x15 tt"], c:
[	
	{ div:["c w41"], case_vw_val:["Client's Spouse Name",":v:clients:spouse_fullname",""] },
	{ div:["c w21 ll"], case_vw_val_cat:["Client's Spouse Profession","",":v:clients:spouse_profession"," %0"] },
	{ div:["e"] }
]};

te["case_client_vw_id_"] = { c:
[
	
	{ div:["x15 clk_client"], case_contact_vw_id_:
	[
":v:clients:contact_fullname",":v:clients:contact_age",":v:clients:contact_age_group",":v:clients:contact_dob",
":v:clients:contact_location",":v:clients:contact_sex",
":v:clients:contact_landmark",":v:clients:contact_nationality",
":v:clients:contact_national_id_type",":v:clients:contact_national_id",":v:clients:contact_lang",
":v:clients:contact_is_refugee::yesno:2", ":v:clients:contact_tribe",
":v:clients:contact_phone",":v:clients:contact_phone2",":v:clients:contact_email"
	]}, 

	{ div:["x15 mt t bt_"], c:
        [
                { div:["c w20"], case_vw_val_cat:["Reporter's Relationship with Client","",":v:clients:relationship"] },
                { div:["c w42 ll"], case_vw_val:["Relationship Comment",":v:clients:relationship_comment"] },
                { div:["e"] }
        ]},
        
	{ div:["x15 bt_ mt t"], c:
	[	
		{ div:["c w20"], case_vw_val_cat:["Number of Adult <br/>in Household","",":v:clients:household_adults"] },
		{ div:["c w20 ll"], case_vw_val_cat:["Household<br/>Type","",":v:clients:household"] },
		{ div:["c w21 ll"], case_vw_val_cat:["Head of Household<br/>Occupation","",":v:clients:household_head_occupation"] },
		{ div:["e"] }
	]},
	
	{ div:["x15 tt"], c:
        [
                { div:["c w41"], case_vw_val:["Parent/Guardian's Name",":v:clients:guardian_fullname"] },
                { div:["c w21 ll"], case_vw_val:["Parent/Guardian's Marital Status",":v:clients:guardian_marital"] },
                { div:["e"] }
        ]},

        { div:["x15 tt"], c:
        [
                { div:["c w20"], case_vw_val_cat:["Parent/Guardian's  Identification Number","",":v:clients:guardian_national_id"] },
                { div:["e"] }
        ]},

	{ div:["x15 bt_ mt t"], c:
	[	
		{ div:["c w20"], case_vw_val_cat:["Client's Health Status","",":v:clients:health"] },
		{ div:["c w20 ll"], case_vw_val_cat:["Client's HIV Status","",":v:clients:hiv"] },
		{ div:["c w21 ll"], case_vw_val_cat:["Client's Marital Status","",":v:clients:marital"] },
		{ div:["e"] }
	]},

	{ div:[], usub:["case_client_vw_sub_spouse,case_client_vw_sub_spouse,case_client_vw_sub_spouse,case_client_vw_sub_spouse,case_client_vw_sub_spouse", "r_", ":v:clients:marital_id", MARITAL_STATUS_WITH_SPOUSE_ID] },

	{ div:["x15 bt_ mt t","va"], c:
	[
		{ div:[], case_vw_val:["Is the Client attending school?",":v:clients:in_school::yesno:2"] },
	]},
	
	{ div:[], usub:["case_client_vw_sub_inschool_no,case_client_vw_sub_inschool_yes","r_",":v:clients:in_school","0,1"] },
		
	{ div:["x15 bt_ mt t","va"], c:
	[
		{ div:[], case_vw_val:["Is the Client Disabled?",":v:clients:is_disabled::yesno:2"] },
	]},

	{ div:[], usub:["case_client_vw_sub_disabled","r_",":v:clients:is_disabled","1"] },
	
]};

te["case_client_vw_id_print"] = { div:["x15"], c:
[
	{ s:["x y h3 b ","Client Details"] }, 
	{ case_client_vw_id_:[] }, 
	{ div:["page-break"] }
]};

te["case_client_vw_id"] = { div:["w66 ma bd sh__ y gw_","vddvw"], ev:["_undd"], c:
[
	{ div:["x15 y"], c:
	[
		{ s:["c x yy h3 b","Client Details"] },
		{ ac:["d ay","","_uvp","x bd cb",""], c:[ { s:["c h y03","&Cross;"] }, { s:["c x y g","Close"] }, { div:["e"] } ] },
		// { div:["d xx ay","va"], ac:["r05","client_ed-clients-vp","_u","xx y gww cb bd","Edit"], c:[ { arg:["",".id","%0"] } ] },
		{ div:["e"] }
	]},
	{ case_client_vw_id_:[] }
]};

// -----------------------------

function case_client_del_ufn (el, u, a, r, m)
{
	var coll = __(el,"clients_case").previousSibling.childNodes;
	var contact_id = valf (r,":v:clients:contact_id");
	for (var i=0; i<coll.length; i++)
	{
		var el = _(coll[i],"_is_client","input","name");
		if (el && el.value==contact_id) el.checked = false;
	}
}


