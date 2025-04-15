

te["reporter_uuid_arg"] = { arg:["","reporter_uuid_id","%0"] };

te["reporter_uuid"] = { p:["g","o"], c:[ { arg:["","reporter_uuid_id","%0"] } ] };

te["reporter_disposition_vw_r"] = { div:["x y gbn"], c:
[
	{ contact_vw_rv:[":v:reporters:contact_fullname", ":v:reporters:contact_age_group", ":v:reporters:contact_sex", ":v:reporters:contact_location", ":v:reporters:contact_landmark"] },
	{ contact_vw_rv_phone:[":v:reporters:contact_phone", ":v:reporters:contact_email"] },
	{ p:["g","o"], arg:["","reporter_id","%0"] }
]}

te["reporter_not_selected"] = { c:
[
	{ div:["x20 t b20","va"], c:
	[
		{ div:["c x t02"], ac:["","","_uvw","h2 x y bd16 gb cw micon","arrow_back"] }, // { u:[null] },	
		{ s:["c x08 tt n cr","Select a Reporter first. Then try again."] },
		{ div:["e"] }
	]},

]};

te["case_form_reporter_r_"] = { c:
[
	{ div:["","ve"], c:
	[
		{ input:["g","","case_form_a","1","radio"] },
		{ li:["x y bd cb gbn","reporter_ed-reporters-^"], ev:["_vp"], c:
		[
			{ contact_vw_rv:[":v:reporters:contact_fullname", ":v:reporters:contact_age_group", ":v:reporters:contact_sex", ":v:reporters:contact_location", ":v:reporters:contact_landmark"] },
			{ contact_vw_rv_phone:[":v:reporters:contact_phone", ":v:reporters:contact_email"] },
			{ div:["x btn"], c:
			[
				{ input:["g","","_is_client",":v:reporters:contact_id","checkbox",":v:reporters:is_client"] },
				{ ac:["ao r w20","","_reporter_isclient","w20 x y",""], c:
				[
					{ div:["c w01_"], s:["chk",""] },
					{ s:["c xx","Reporter is also a Client"] },
					{ div:["e"] }
				]}
			]},
			{ div:["x savl"], s:["w20 x y go cw bd","..."] },
			{ div:[], c:[ { p:["c x","nb"] }, { div:["e"] } ] },
			{ div:["g"], arg:["",".id","%0"] }
		]},
		{ div:["g"], arg:["","",null] } 
	]},
	{ p:["","o"], c:
	[ 
		{ arg:["",null,"%0"] },
		// { arg:["","uuid",":v:reporters:uuid"] } // use uuid from case_form
	]}
]};

te["case_form_reporter_"] = { c:
[
	{ div:["t"], c:
	[
		{ s:["xx yy b n",null] },
		{ div:["e"] }
	]},
	{ div:["","va"], u:[null] },
	{ arg:["","",null] }
]};


te["case_form_reporter_r"] = { case_form_reporter_r_:["case_form_reporter_r-reporters-va--@","reporter_id"] };

te["case_form_reporter_followup_r"] = { case_form_reporter_r_:["case_form_reporter_followup_r-reporters-va--@","reporter_uuid_id"] };

te["case_form_reporter_new_case_r"] = { case_form_reporter_r_:["case_form_reporter_new_case_r-reporters-va--@","reporter_uuid_id"] };


te["case_form_reporter"] = { case_form_reporter_:["Reporter","case_form_reporter_r","case_form_reporter_r"] };

te["case_form_reporter_followup"] = { case_form_reporter_:["Followup By","case_form_reporter_followup_r","case_form_reporter_followup_r"] };

te["case_form_reporter_new_case"] = { case_form_reporter_:["Reporter","case_form_reporter_new_case_r","case_form_reporter_new_case_r"] };

// ----------------------------------------------------	

te["case_reporter_ed_"] = { div:["w68 ma sh__ gw_"], c:
[	
	{ div:["x15 tt"], c:
	[
		{ s:["c xx y12 n b",null] },
		{ ac:["d","","_uvp","xx y08 h cb","&Cross;"] },
		{ div:["e"] }
	]},

	{ div:["","ve"], c:
	[
		{ div:["x25 t"], c:[ { p:["c w55","nb"], u:["nb","reporters_nb"] }, { div:["e"] } ] },

		{ p:["x25","contact"], case_contact_ed_r_:
		[
"Reporter's Name",":v:reporters:contact_fullname","Enter Reporter's Names",
":v:reporters:contact_age",":v:reporters:contact_dob",":v:reporters:contact_dob",":v:reporters:contact_age_group_id",":v:reporters:contact_age_group"," %0", 
":v:reporters:contact_location_id",":v:reporters:contact_location"," %0",
":v:reporters:contact_sex_id",":v:reporters:contact_sex"," %0",  
":v:reporters:contact_landmark",
":v:reporters:contact_nationality_id",":v:reporters:contact_nationality"," %0",
":v:reporters:contact_national_id_type_id",":v:reporters:contact_national_id_type"," %0",
":v:reporters:contact_national_id", 
":v:reporters:contact_lang_id",":v:reporters:contact_lang"," %0", 
"Is the Reporter a Refugee?",":v:reporters:contact_is_refugee",
":v:reporters:contact_tribe_id",":v:reporters:contact_tribe"," %0",
":v:reporters:contact_phone",
":v:reporters:contact_phone2", 
":v:reporters:contact_email"
		]},			
				
		{ div:["w63 x25 t30 b20"], vp_sav:[null,null,null,null,null,null,null] }
	]}
]};

te["case_reporter_ed"] = { case_reporter_ed_:["Edit Reporter","reporter_ed-reporters","_activity_case_postj","Update","Updating...","","_uvp","Cancel"] };

te["case_reporter_new"] = { case_reporter_ed_:["New Reporter","reporter_new-reporters","_activity_case_postj","Create","Creating...","","_uvp","Cancel"] };

// --------------------------------------------------------------------------------------------

te["case_vw_reporter_r_"] = {  c: 
[
	{ input:["g","","case_vw_a","%0","radio",""] },
	{ li:[null,"reporter_vw_id-reporters-^"], ev:["_vp"], s:["",""], c:
	[
		{ div:[], c:
		[
			{ div:["d w07"], s:["abs t",""], c:[ { s:[":v:reporters:is_client::reporter_is_client:3",":v:reporters:is_client::reporter_is_client:4"] } ] }, 
			{ div:["e"] }
		]},
		{ contact_vw_rv:[":v:reporters:contact_fullname", ":v:reporters:contact_age_group", ":v:reporters:contact_sex", ":v:reporters:contact_location",":v:reporters:contact_landmark"] },
		{ contact_vw_rv_phone:[":v:reporters:contact_phone", ":v:reporters:contact_email"] },
		
		{ div:["g"], arg:["",".id","%0"] }
	]},
	{ div:["g"], arg:["","","case_vw_reporter_r_-reporters-va--@"] },
]};

te["case_vw_reporter_r"] = { div:["mb","va"], case_vw_reporter_r_:["xx y bd cb gws_"] };

te["case_vw_reporter_uuid_r"] = { div:["mb","va"], case_vw_reporter_r_:["xx y bd cb gbn"] };

te["case_vw_reporter_uuid"] = { c:
[
	{ div:["t"], c:
	[
		{ s:["xx yy b n","Followup By"] },
		// todo: link: change contact -> { new contact, search contact }
		{ div:["e"] }
	]},
	{ u:["case_vw_reporter_uuid_r","reporters"] },
]};

// ----

te["case_reporter_vw_id_"] = { c:
[
	{ div:["x15 b10"], case_contact_vw_id_:
	[
":v:reporters:contact_fullname",":v:reporters:contact_age",":v:reporters:contact_age_group",":v:reporters:contact_dob",
":v:reporters:contact_location",":v:reporters:contact_sex",
":v:reporters:contact_landmark",":v:reporters:contact_nationality",
":v:reporters:contact_national_id_type",":v:reporters:contact_national_id", ":v:reporters:contact_lang",
":v:reporters:contact_is_refugee::yesno:2", ":v:reporters:contact_tribe",
":v:reporters:contact_phone",":v:reporters:contact_phone2",":v:reporters:contact_email"
	]}
]};

te["case_reporter_vw_id_print"] = { div:["x15"], c:
[
	{ s:["x y h3 b ","Reporter Details"] }, 
	{ case_reporter_vw_id_:[] }, 
	{ div:["page-break"] }
]};

te["case_reporter_vw_id"] = { div:["w66 ma bd sh__ y gw_","vddvw"], ev:["_undd"], c:
[
	{ div:["x15 y"], c:
	[
		{ s:["c x yy h3 b","Reporter Details"] },
		{ ac:["d ay","","_uvp","x bd cb",""], c:[ { s:["c h y03","&Cross;"] }, { s:["c x y g","Close"] }, { div:["e"] } ] },
		// { div:["d xx ay","va"], ac:["r05","client_ed-clients-vp","_u","xx y gww cb bd","Edit"], c:[ { arg:["",".id","%0"] } ] },
		{ div:["e"] }
	]},
	{ case_reporter_vw_id_:[] }
]};

// -------------------

te["reporter_isclient_ufn"] = { ufn:["reporter_isclient_ufn"] };

function reporter_isclient_ufn (el, u, a, r, m)
{
	nd (el, te[el.nextSibling.value], [], r, [0]);
	var p = _(__(el,"ve"), "clients_case").childNodes[1];
	var coll = p.childNodes;
	if (ra["clients"].length<1) return;
	var client_id = ra["clients"][0][0];
	var case_id_ = valf (ra["clients"][0], ":v:clients:case_id_");
	for (var i=0; i<coll.length; i++)
	{
		var el = coll[i].firstChild;
		// console.log (">>>>"+el.firstChild.value+","+client_id)
		if (el && el.id=="ve" && el.firstChild && el.firstChild.value==client_id) p.removeChild (coll[i]);
	}
	if (case_id_!=-9) var el = nd (p, te["case_form_client_r"], [], ra["clients"][0], [0]);
	// todo open vp
}

function _reporter_isclient (ev)
{
	var p = __(this,"ve")
	var p_ = __(p,"vfvwm");
	var o = {};
	var o_ = {};
	jso (p_.firstChild, o); 		// channel data
	jso (__(p.parentNode,"ve"), o_); 	// get case_id 
	argv (p.nextSibling, o); 		// get reporter_id 
	o["case_id_"] = o_[".id"];
	o["case_uuid"] = o_["uuid"];
	if (this.previousSibling.checked) { o["case_id_"]="-9"; }
	if (o["reporter_uuid_id"]) o["reporter_id"] = o["reporter_uuid_id"];
	url (p, "reporter_is_client", "reporters^isclient", o["reporter_id"], null, 2, o, "POST"); // create|del client (from reporter_contact_id)
	boo (ev);
	//console.log (o)
}

