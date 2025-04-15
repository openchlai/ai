
te["case_perpetrator_del"] = { c:
[
	{ div:["l cr gp"], c:
	[
		{ s:["c x y","Perpetrator Deleted"] },
		{ ac:["d ay ga","","_rm","x y h2","&Cross;"] },
		{ div:["e"] }
	]},
]};

te["case_form_perpetrator_r_"] = { c:
[
	{ div:["","ve"], c:
	[
		{ input:["g","","case_form_a","%0","radio"] },
		{ li:["x y bd cb gbn","perpetrator_ed-perpetrators-^"], ev:["_vp"], c:
		[
			{ div:[], c:
			[
				{ div:["d w03"], ac:["abs w03","perpetrator_del-perpetrators^del","_del","cb h2",""], c:
				[
					{ s:["x y h2 tc","&Cross;"] },
					{ div:[], c:[ { arg:["",".id","%0"] } ] }
				]},
				{ div:["e"] }
			]},
			{ contact_vw_rv:[":v:perpetrators:contact_fullname", ":v:perpetrators:contact_age_group", ":v:perpetrators:contact_sex", ":v:perpetrators:contact_location", ":v:clie	nts:contact_landmark"] },
			{ contact_vw_rv_phone:[":v:perpetrators:contact_phone", ":v:perpetrators:contact_email"] },
			{ div:["g"], arg:["",".id","%0"] }
		]},
		{ div:["g"], arg:["","","case_form_perpetrator_r_-perpetrators-va--@"] },
	]},
	{ div:[], arg:["o","perpetrator_id","%0"] }
]};

te["case_form_perpetrator_r"] = { div:["mb","va"], case_form_perpetrator_r_:[] };

// ----------------------------

te["case_perp_marital_sel_sub"] = { div:["","sub"], c:
[
	{ arg:["case_perpetrator_ed_sub_spouse,case_perpetrator_ed_sub_spouse,case_perpetrator_ed_sub_spouse,case_perpetrator_ed_sub_spouse,case_perpetrator_ed_sub_spouse-r_-ve-_case_perp_spouse_", "", MARITAL_STATUS_WITH_SPOUSE_ID] },
]};

te["case_perp_marital_tag_txa"] = { case_enum_tag_txa_:["w21 xx tt b05","fullname__","Select Marital Status","marital_id"] };

te["case_perp_marital_enum"] = { case_enum_ls:["x y",null,"", "tag-r_--o-case_perp_marital_tag_txa-%1-marital_id-%0-%2", "category_ls-subcategories", "c w17", 
"case_perp_marital_tag_txa","r_", 
null, "case_perp_marital_tag_txa",null,"marital_id",null," %2", 
MARITAL_STATUS_ROOT_ID, "fullname", "noop", 
"dd w21 gw_ ba_b", 
"case_perp_marital_sel_sub"] };

// ---- 

te["case_perpetrator_ed_sub_spouse"] = { div:["tt"], c:
[	
	{ div:["c w41"], case_txt_:["Spouse Name","gws w41 x tt b05","spouse_fullname",":v:perpetrators:spouse_fullname",""] },
	{ div:["c w21 ll"], case_spouse_employment_enum:["Spouse Profession",":v:perpetrators:spouse_profession_id",":v:perpetrators:spouse_profession"," %0"] },
	{ div:["e"] }
]};

// ---- 

te["case_perpetrator_ed_"] = { div:["w68 ma mb sh__ gw_"], c:
[
	{ div:["x15 tt"], c:
	[
		{ s:["c xx y12 n b",null] },
		{ ac:["d","","_uvp","xx y08 h cb","&Cross;"] },
		{ div:["e"] }
	]},
			
	{ div:["","ve"], c:
	[
		{ div:["x25 t"], c:[ { p:["c w55","nb"], u:["nb","perpetrators_nb"] }, { div:["e"] } ] },
		
		{ p:["x25","contact"], case_contact_ed_r_:
		[
"Perpetrator's Name",":v:perpetrators:contact_fullname","Enter Perpetrator's Names",
":v:perpetrators:contact_age",":v:perpetrators:contact_dob",":v:perpetrators:contact_dob",":v:perpetrators:contact_age_group_id",":v:perpetrators:contact_age_group"," %0", 
":v:perpetrators:contact_location_id",":v:perpetrators:contact_location"," %0",
":v:perpetrators:contact_sex_id",":v:perpetrators:contact_sex"," %0",  
":v:perpetrators:contact_landmark",
":v:perpetrators:contact_nationality_id",":v:perpetrators:contact_nationality"," %0",
":v:perpetrators:contact_national_id_type_id",":v:perpetrators:contact_national_id_type"," %0",
":v:perpetrators:contact_national_id", 
":v:perpetrators:contact_lang_id",":v:perpetrators:contact_lang"," %0", 
"Is the Perpetrator a Refugee?",":v:perpetrators:contact_is_refugee",
":v:perpetrators:contact_tribe_id",":v:perpetrators:contact_tribe"," %0",
":v:perpetrators:contact_phone",
":v:perpetrators:contact_phone2", 
":v:perpetrators:contact_email", 
		]},
	
		{ div:["x25 tt"], c:
		[
			{ div:["c w20"], case_rela_enum:["Relationship with Client?",":v:perpetrators:relationship_id",":v:perpetrators:relationship"," %0"] },
			{ div:["c w20 ll"], case_shareshome_enum:["Shares Home with Client?",":v:perpetrators:shareshome_id",":v:perpetrators:shareshome"," %0"] }, 
			{ div:["e"] }
		]},
		
		{ div:["x25 tt"], c:
		[
			{ div:["c w20"], case_health_enum:["Health Status",":v:perpetrators:health_id",":v:perpetrators:health"," %0"] },
			{ div:["c w20 ll"], case_employment_enum:["Perpetrator's Profession",":v:perpetrators:employment_id",":v:perpetrators:employment"," %0"] },	
			{ div:["c w21 ll"], case_perp_marital_enum:["Perpetrator's Marital Status",":v:perpetrators:marital_id",":v:perpetrators:marital"," %0"] },
			{ div:["e"] }
		]},
		
		{ p:["x25","_case_perp_spouse_"], usub:["case_perpetrator_ed_sub_spouse,case_perpetrator_ed_sub_spouse,case_perpetrator_ed_sub_spouse,case_perpetrator_ed_sub_spouse,case_perpetrator_ed_sub_spouse", "r_", ":v:perpetrators:marital_id", MARITAL_STATUS_WITH_SPOUSE_ID] },
			
		{ div:["x25 tt"], c:
		[
			{ div:["c w41"], case_txt_:["Perpetrator's Guardian's Name","gws w41 x tt b05","guardian_fullname",":v:perpetrators:guardian_fullname","Enter Perpetrator's Guardian Name"] },
			
			{ div:["e"] }
		]},
			
		{ div:["x25 tt"], c:
		[
			{ s:["x y", "Additional Details"] },
			{ p:["w63 gws bd","o"], c:[ { textarea:["gws w63 h11 x y08","","notes",":v:perpetrators:notes","Enter Additional Details"] } ] },
			{ div:["e"] }
		]},
		
		{ div:["x25 t30 b20"], vp_sav:[null,null,null,null,null,null,null] }
	]}
]};

te["case_perpetrator_ed"] = { case_perpetrator_ed_:["Edit Perpetrator Details","perpetrator_ed-perpetrators","_activity_case_postj","Update","Updating...", "perpetrator_vw_id-perpetrators-vp","_u","Cancel"] };

te["case_perpetrator_new"] = { case_perpetrator_ed_:["New Perpetrator","perpetrator_new-perpetrators","_activity_case_postj","Create","Creating...","","_uvp","Cancel"] };

// --------------------------------------------------------------------------------------------

te["case_vw_perpetrator_r_"] = {  c: // 
[
	{ input:["g","","case_vw_a","%0","radio",""] },
	{ li:["xx y bd cb gws_","perpetrator_vw_id-perpetrators-^"], ev:["_vp"], s:["",""], c:
	[
		{ contact_vw_rv:[":v:perpetrators:contact_fullname", ":v:perpetrators:contact_age_group", ":v:perpetrators:contact_sex", ":v:perpetrators:contact_location", ":v:perpetrators:contact_landmark"] },
		{ contact_vw_rv_phone:[":v:perpetrators:contact_phone", ":v:perpetrators:contact_email"] },
		{ div:["g"], arg:["",".id","%0"] }
	]},
	{ div:["g"], arg:["","","case_vw_perpetrator_r_-perpetrators-va--@"] },
]};

te["case_vw_perpetrator_r"] = { div:["mb","va"], case_vw_perpetrator_r_:[] };

// -----------------------------

te["case_perpetrator_vw_sub_spouse"] = { div:["x15 tt"], c:
[	
	{ div:["c w41"], case_vw_val:["Spouse Name",":v:perpetrators:spouse_fullname",""] },
	{ div:["c w21 ll"], case_vw_val_cat:["Spouse Profession","",":v:perpetrators:spouse_profession"," %0"] },
	{ div:["e"] }
]};

te["case_perpetrator_vw_id_"] = { c:
[
	
	{ div:["x15 b10"], case_contact_vw_id_:
	[
":v:perpetrators:contact_fullname",":v:perpetrators:contact_age",":v:perpetrators:contact_age_group",":v:reporters:contact_dob",
":v:perpetrators:contact_location",":v:perpetrators:contact_sex",
":v:perpetrators:contact_landmark",":v:perpetrators:contact_nationality",
":v:perpetrators:contact_national_id_type",":v:perpetrators:contact_national_id",":v:perpetrators:contact_lang",
":v:perpetrators:contact_is_refugee::yesno:2", ":v:perpetrators:contact_tribe",
":v:perpetrators:contact_phone",":v:perpetrators:contact_phone2",":v:perpetrators:contact_email"
	]},

	{ div:["x15"], s:["bt_ tt",""], c:
	[
		{ div:["c w20"], case_vw_val_cat:["Relationship with Client?","",":v:perpetrators:relationship"] },
		{ div:["c w20 ll"], case_vw_val_cat:["Shares Home with Client?","",":v:perpetrators:shareshome"] },
		{ div:["e"] }
	]},
	
	{ div:["x15 tt"], c:
	[
		{ div:["c w20"], case_vw_val_cat:["Health Status","",":v:perpetrators:health"] },
		{ div:["c w20 ll"], case_vw_val_cat:["Perpetrator's Profession","",":v:perpetrators:employment"] },
		{ div:["c w21 ll"], case_vw_val_cat:["Perpetrator's Marital Status","",":v:perpetrators:marital"] },
		{ div:["e"] }
	]},
	
	{ div:[], usub:["case_perpetrator_vw_sub_spouse,case_perpetrator_vw_sub_spouse,case_perpetrator_vw_sub_spouse,case_perpetrator_vw_sub_spouse,case_perpetrator_vw_sub_spouse"
,"r_", ":v:perpetrators:marital_id", MARITAL_STATUS_WITH_SPOUSE_ID] },
	
	{ div:["x15 tt"], c:
	[
		{ div:["c w41"], case_vw_val:["Perpetrator's Guardian's Name",":v:perpetrators:guardian_fullname"] },	
		{ div:["e"] }
	]},
			
	{ div:["x15 yy"], c:
	[
		{ div:["w63"], case_vw_val:["Additional Details",":v:perpetrators:notes"] },
		{ div:["e"] }
	]}
]};

te["case_perpetrator_vw_id_print"] = { div:["x15"], c:
[
	{ s:["x y h3 b ","Perpetrator Details"] }, 
	{ case_perpetrator_vw_id_:[] }, 
	{ div:["page-break"] }
]};

te["case_perpetrator_vw_id"] = { div:["w66 ma bd sh__ y gw_","vddvw"], ev:["_undd"], c:
[
	{ div:["x15 y"], c:
	[
		{ s:["c x yy h3 b","Perpetrator Details"] },
		{ ac:["d ay","","_uvp","x bd cb",""], c:[ { s:["c h y03","&Cross;"] }, { s:["c x y g","Close"] }, { div:["e"] } ] },
		// { div:["d xx ay","va"], ac:["r05","client_ed-clients-vp","_u","xx y gww cb bd","Edit"], c:[ { arg:["",".id","%0"] } ] },
		{ div:["e"] }
	]},
	{ case_perpetrator_vw_id_:[] }
]};

