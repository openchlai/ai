
te["category_ed_"] = { div:["w48 ma mb sh__ gw_"], c:
[
	{ div:["x15 tt"], c:
	[
		{ s:["c xx y12 n b",null] },
		{ ac:["d","","_uvp","xx y08 h cb","&Cross;"] },
		{ div:["e"] }
	]},
	{ div:["","ve"], c:
	[
		{ div:["x20"], c:[ { p:["c","nb"], u:["nb","categories_nb"] }, { div:["e"] } ] },
		{ div:["x20 t"], c:
		[ 
			{ s:["c w10 x y cd","Name"] }, 
			{ s:["c w25 x y cb",":v:categories:name"] }, 
			{ div:["e"] }
		]},
		{ div:["x20 t15"], c:
		[ 
			{ s:["c w10 x y cd","Parent"] }, 
			{ s:["c w25 x y cb",":v:categories:category_name"] }, 
			{ div:["e"] }
		]},
		{ div:["x20 t15"], c:
		[ 
			{ s:["c w10 x y cd","Full Name"] }, 
			{ s:["c w25 x y cb",":v:categories:full_name"] }, 
			{ div:["e"] }
		]},
		{ div:["x20 y15"], c:
		[
			{ s:["c x y cd","Active"] },
			{ div:["d x","tag-r_--o--::is_active:0:1-isactive-%0-"], c:
			[
				{ li:["ba w32 gw_","va"], c:[ { div:[], ev:["_dd"], c: // ls
				[
					{ p:["c w27 b03","o"], uchk:["tag",":v:categories:isactive","","", ""," ::is_active:0:1","isactive"," %0",""] },
					{ div:["d w02 x y"],  c:[ { div:["h02 w02 awb"] } ] },
					{ div:["e"] }
				]} ]},			
				{ div:["dd w15 mtn1 ba gw_ cb","vdd"], ev:["_undd"], c: // 
				[
					{ uchk:["user_role_r","","is_active"] }
				]}
			]},
			{ div:["e"] }
		]},
		{ div:["x25 y20"], vp_sav:[null,null,null,null,null,null,null] }
	]},
]};

te["category_ed"] = { category_ed_:["Edit Category","category_ed-subcategories","_postj","Update","Updating...","category_vw_id-categories-vp","_u","Cancel"] };

// ------------------------------------------

te["category_vw_r"] = { c:
[
	{ div:["x20"], c:
	[ 
		{ div:["d w04 x","va"], ac:["abs t ad","category_ed-categories-vp","_u","w04 y ba cb tc","Edit"], c:[ { arg:["",".id","%0"] } ] },
		{ div:["e"] }
	]},
	{ div:["x20"], c:[ { u:["nb","categories_nb"] }, { div:["e"] } ] },
	{ div:["x20 t"], c:
	[ 
		{ s:["c w10 x y cd","Name"] }, 
		{ s:["c w25 x y cb",":v:categories:name"] }, 
		{ div:["e"] }
	]},
	{ div:["x20 t15"], c:
	[ 
		{ s:["c w10 x y cd","Parent"] }, 
		{ s:["c w25 x y cb",":v:categories:category_name"] }, 
		{ div:["e"] }
	]},
	{ div:["x20 t15"], c:
	[ 
		{ s:["c w10 x y cd","Full Name"] }, 
		{ div:["c w25 x y cb"], uval:["",":v:categories:fullname"] }, 
		{ div:["e"] }
	]},
	{ div:["x20 t15 b25"], c:
	[ 
		{ s:["c w10 x y cd","Status"] }, 
		{ s:["c w25 x y cb",":v:categories:isactive::is_active:1"] }, 
		{ div:["e"] }
	]}
]};

te["category_vw_id"] = { vpvw:["w48 ma sh__ gw_",  "Category","noop",          "noop","category_vw_r"] };

// -------------------------------------------------------------------------------

te["category_ls_footer"] = { div:["x gw_ mt"], c:
[
	{ s:["c x y cd s","%2"] },
	{ s:["c y cd s","-"] },
	{ s:["c x y cd s","%3"] },
	{ s:["c y cd s","of"] }, 
	{ s:["c x y cd s","%4"] },
	{ div:["d t03"], c:[ { ac:["nav","category_ls-subcategories","_nav","dh",""], c:[ { div:["da dr_"] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] },
	{ div:["d t03"], c:[ { aci:["nav","category_ls-subcategories","_nav","dh","prev",""], c:[ { div:["da dl_"] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] },
	{ div:["e"] }
]};

te["category_ls_r"] = { ac:["ay","","_sel","xx cb",""], c:
[
	{ div:["x y07"], uhilite:[":v:categories:fullname"] },
	{ div:["e"], c:[ { arg:["id-0","","%0"] }, { arg:["fullname-1","",":v:categories:fullname"] }, { arg:["fullname_id-2","",":v:categories:fullname_id"] } ] }
]};

te["category_ls_k"] = { div:["g"], c:
[
	{ arg:["","root_id_",":k:subcategories_k:root_id_:2"] },
	{ arg:["","level",":k:subcategories_k:level:2"] },
	{ arg:["","fullname__",":k:subcategories_k:fullname:2"] },
	{ p:["","e"], c:[ { arg:["","_c","%1"] }, { arg:["","sort","%6"] } ] }
]};

te["category_ls"] = { list:["end","end","","category_ls_k","category_ls_r","subcategories","category_ls_footer"] },

te["category_lsh_footer"] = { div:["bl_"], c:
[
	{ s:["c w02 tt bb_"," "] },
	{ s:["c x y cd s","%2"] },
	{ s:["c y cd s","-"] },
	{ s:["c x y cd s","%3"] },
	{ s:["c y cd s","of"] }, 
	{ s:["c x y cd s","%4"] },
	{ div:["c t03"], c:[ { aci:["nav","category_lsh-subcategories","_nav","dh","prev",""], c:[ { div:["da dl_"] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] },
	{ div:["c t03"], c:[ { ac:["nav","category_lsh-subcategories","_nav","dh",""], c:[ { div:["da dr_"] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] },
	{ div:["e"] }
]};

te["category_lsh_r_loc"] = { s:["xx yy cd",":v:categories:level::loclev:1"] };

te["category_lsh_r"] = { c:
[
	{ div:["t","vg"], s:["content-hidden",""], c:
	[
		{ s:["c w02 tt bb_"," "] },
		//{ ac:["c ad r05 content-hidden_","category_lsh-categories","_g","x y03 n ga cb ba_","&plus;"], c:[ { arg:[".id","","%0"] }, { arg:["_c","","50"] } ] },
		//{ ac:["c ad r05 content-shown_","category_lsh-categories","_g","x y03 n ga cb ba_","&minus;"], c:[ { arg:[".id","","%0"] } ] },
		{ input:["g","","category","%0","radio"] },
		{ div:["c r","va"], c:
		[
			{ ac:["aa","category_lsh_node-categories","_sel_nest","x07 y cb",""], c:
			[ 
				{ s:["",":v:categories:name"] },
				{ div:["e"], c:[ { arg:["id-0","","%0"] }, { arg:["fullname-1","",":v:categories:fullname"] }, { arg:["fullname_id-2","",":v:categories:fullname_id"] }, { arg:["level-3","",":v:categories:level"] }  ] }
			]}
		]},
		{ div:["c x15 h01"], u:["nb","subcategories_nb"] },
		{ div:["e"] }
	]},
	{ div:["g","vs"] }
]};

te["category_lsh_k"] = { div:["g"], c:
[
	{ arg:["","category_id_",":k:subcategories_k:category_id_:2"] },
	{ p:["","e"], c:[ { arg:["","_c","%1"] }, ] }
]};

te["category_lsh"] = { c:
[
	//{ list:["end","end","","category_lsh_k","category_lsh_r","subcategories","category_lsh_footer"] }
	{ div:["bl_ h01"], c:
	[
		{ div:["e"] }
	]},
	{ div:[] }, // nb
	{ div:[], c:
	[
		{ p:["","vc"], category_lsh_k:[] }, // header
		{ div:["bl_"], u:["category_lsh_r","subcategories"] },
	]},
	{ category_lsh_footer:[] }
]}

te["category_lsh_node"] = { c:
[
	{ div:[], c:
	[
		{ ac:["c aa t","category_lsh_node-categories","_sel_nest","xx y cb gws",""], c:
		[
			{ s:["",":v:categories:name"] },
			{ div:["e"], c:[ { arg:["id-0","","%0"] }, { arg:["fullname-1","",":v:categories:fullname"] }, { arg:["fullname_id-2","",":v:categories:fullname_id"] }, { arg:["level-3","",":v:categories:level"] } ] }
		]},
		{ div:["c"], usub:["category_lsh_r_loc","r_",":v:categories:root_id",LOCATION_ROOT_ID] },  
		{ div:["e"] }
	]},	
	{ div:["ml2","vs"], u:["category_lsh","subcategories_ctx"] },
]};

te["category_lsh_main"] = { c:
[
	{ div:["","vb"], c:
	[
		{ div:["d w03 tt r15","va"], c:
		[
			{ input:["g","","case_f_vw_t","0","radio","1"] },
			{ ac:["ay tab abs w03","category_lsh_main-categories","_tab","cb ba_b gw",""], c:
			[
				{ s:["x y h3 micon","account_tree"] },
				{ div:[], arg:["",".id",":k:categories_k:root_id_:2"] }
			]}
		]},
		{ div:["d w03 tt g","va"], c:
		[
			{ input:["g","","case_f_vw_t","1","radio"] },
			{ ac:["ay tab abs w03","category_ls-categories","_tab","cb",""], c:
			[
				{ s:["x y h3 micon","list"] },
				{ div:[], arg:["",".id",":k:categories_k:root_id_:2"] }
			]}
		]},
		{ div:["e"] }
	]},
	{ div:[], c:
	[
		{ div:[], c:
		[
			{ input:["g","","category_ls_vt","0","radio","1"] }, 
			{ div:["tabv x15 b10","vs"], u:["category_lsh_node","categories"] }
		]},
		{ div:[], c:
		[
			{ input:["g","","category_ls_vt","0","radio"] },
			{ div:["tabv t30","vt"] } //, category_ls:[] }
		]}
	]}
]};

// -------------------------------------------------------------------------------

te["category_lc_footer"] = { div:["x gws mt"], c:
[
	{ s:["c x y cd s","%3"] },
	{ s:["c y cd s","of"] }, 
	{ s:["c x y cd s","%4"] },
	{ div:["d t03"], c:[ { ac:["nav","category_lc-subcategories","_nav","dh",""], c:[ { div:["da dr_"] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] },
	{ div:["d t03"], c:[ { aci:["nav","category_lc-subcategories","_nav","dh","prev",""], c:[ { div:["da dl_"] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] },
	{ div:["e"] }
]};

te["category_lc_r"] = { div:[], c: 
[
	{ input:["g","category_id","","%0","checkbox",":k:categories_chk:category_id::0"] },
	{ ac:["r ay w60","","_chk","xx y07 cb",""], c:
	[ 
		{ div:["abs t03 w02"], s:["chk",""] },
		{ div:["ml2"], uhilite:[":v:categories:fullname"] },
		{ div:["e"], c:[ { arg:["fullname-1","",":v:categories:fullname"] }, { arg:["fullname_id-2","",":v:categories:fullname_id"] } ] }
	]}
]};

te["category_lc_k"] = { div:["g"], c:
[
	{ arg:["","root_id_",":k:subcategories_k:root_id_:2"] },
	{ arg:["","level",":k:subcategories_k:level:2"] },
	{ arg:["","fullname__",":k:subcategories_k:fullname:2"] },
	{ p:["","e"], c:[ { arg:["","_c","%1"] }, { arg:["","sort","%6"] } ] }
]};

te["category_lc"] = { c:
[
	{ uchkargs:["categories_chk"] },
	{ list:["end","end","mh30","category_lc_k","category_lc_r","subcategories","category_lc_footer"] }
]};

te["category_lc_main_"] = { c:
[
	{ div:["xx mb","va"], c:[ { div:["","category_lc-subcategories"], c:
	[ 
		{ p:["w50 bb_b","txa"], c:[ { input:["w50 x tt b05","fullname__","","","text",""], ev:["","_ky","","_uky"] } ] },
		{ u:[null] } // ky args
	]} ]},
	{ div:["","vd"], category_lc:[] }
]};

// -------------------------------------------------------------------------------

te["category_f_tags"] = { c: 
[
	{ f:["Name",":k:categories_f:fname",		" %0"," name"] },
	{ f:["Parent",":k:categories_f:lname",		" %0"," pname"] },
	{ div:["e"] }
]};

te["category_f"] = { div:["w70 ma bd sh__ xx yy gw"], c: // "vddvw"], ev:["_undd"
[
	{ s:["x12 yy b bb","Filters"] },
	{ div:["x tt b20"], c:
	[
		{ div:["xx yy"], kf_s:["Name","fname",":k:categories_f:name"] },
		{ div:["xx yy"], kf_s:["Parent","lname",":k:categories_f:pname"] },
		{ div:["xx yy"], kf_d:["Created On"," :d:dmy:0: ","created_on",":k:categories_f:created_on","created_on",":k:categories_f:created_on"] },
	]},
	{ div:["x15 yy"], c:
	[
		{ div:["c w06 r02"], c:[ { ac:["ad btn","category_f_tags-categories_f","_applyf","x y w05 gbl bd ba_br cw tc","Apply"] }, { s:["y07 bd b savl","..."] } ] },
		{ div:["c l20","va"], ac:["ay","","_vpcancel","x y w05 ba_bl bd tc cbr","Cancel"], c:[ { p:["g","o"], arg:["",".id",""] } ] },
		{ div:["e"] }
	]}
]};

// -------------------------------------------------------------------------------

te["category_r_new"] = { div:["","va"], c:
[
	{ div:["","ve"], s:["y",""], c:
	[
		{ s:["c w02 tt bb"," "] },
		{ p:["","o"], txt:["c w30 gw ba","w30 x y","","name",""] }, 
		{ div:["c l20 t02"], c:[ { ac:["ad btn","category_new-subcategories","_postj","xx y03 gbl bd ba_br cw tc","Save"] }, { s:["y07 bd b savl","..."] } ] },
		{ div:["c l20 t02"], ac:["aa","","_rm","x y03 tc n cb","&Cross;"], c:[ { p:["g","o"], arg:["",".id",""] } ] },
		{ p:["c t01 x15","nb"] },
		{ p:["e","o"], arg:["","category_id",":v:categories:category_id"] }
	]}
]};

te["category_r"] = { c:
[
	{ div:["t","vg"], s:["content-hidden",""], c:
	[
		{ s:["c w02 tt bb"," "] },
		{ ac:["c ad r05 content-hidden_","subcategory_list-categories","_g","x y03 n ga cb ba_","&plus;"], c:[ { arg:[".id","","%0"] }, { arg:["_c","","50"] } ] },
		{ ac:["c ad r05 content-shown_","subcategory_list-categories","_g","x y03 n ga cb ba_","&minus;"], c:[ { arg:[".id","","%0"] } ] },
		{ input:["g","","category","%0","radio"] },
		{ div:["c r","va"], c:
		[
			{ ac:["aa","category_vw_id-categories","_vp","x07 y cb bd",""], c:
			[ 
				{ s:["",":v:categories:name"] },
				{ div:[], c:[ { arg:["",".id","%0"] } ] },
			]}
		]},
		{ div:["c x15 h01"], u:["nb","subcategories_nb"] },
		{ div:["e"] }
	]},
	{ div:["g","vs"] }
]};

te["category_rr"] = { c:
[
	{ u:["category_r","subcategories"] }, 
	{ div:[] }, // new item
	{ div:["t","va"], c: 
	[
		{ s:["c w02 tt bb"," "] },
		{ ac:["c aa","category_r_new-category_","_ndr","xx y gwd cb","&plus; New"] }, 
		{ div:["g"], c:[ { arg:["category_id-8","",":k:subcategories_k:category_id_:2"] } ] },
		{ div:["e"] }
	]}
]};

te["category_pg"] = { pg:["pgto",null," dh","da dl",null," dh","da dr"] };

te["category_h"] = { uchk:["category_h",":k:categories:"] };

te["category_list_"] = { c:
[
	{ div:[null,"va"], c:
	[
		{ div:["c","va"], ac:["","category_list-categories-vftab","_u","x y cb b h3","Categories"], c:[ { arg:["",".id","0"] } ] },
		{ u:["category_h","categories"] },
		{ div:["e"] }
	]},
	{ div:[], c:[ { u:["nb","category_nb"] }, { div:["e"] } ] }, // nb
	{ div:[], c:
	[
		{ p:["","vc"], c:[  { arg:["","_c","%1"] }, { arg:["","category_id_",null] }, { div:["e"] } ] }, // header
		{ div:["ml3 mb4 bl"], category_rr:[] },
	]},
	{ div:["x20 bt"], c:
	[
		{ div:["d y08"], category_pg:[null,null] },
		{ div:["e"] }
	]} 
]};

te["subcategory_list"] = { category_list_:["g",":k:subcategories_k:category_id_:2","subcategory_list-subcategories","subcategory_list-subcategories"] };

te["category_list"] = { category_list_:["x y","0","category_list-subcategories","category_list-subcategories"] };

te["categories"] = { c:
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
		{ div:[] }, // blank src
	]},
	{ form:[], c:
	[
		{ div:[], c:
		[	
			{ input:["g","","user_vw_vt","0","radio","1"] }, 
			{ p:["tabv x20 y20 gw mm","vftab"], u:["category_list","subcategories_ctx"] } 
		]},
		{ div:[], c:
		[	
			{ input:["g","","user_vw_vt","1","radio"] }, 
			{ p:["tabv gw yy mm","vfvw"] }
		]}
	]}
]};

// -------------------------------------------------------------------------------

function _sel_nest ()
{
	var u = this.id.split ("-");
	var a = {};
	argv (this, a, "id");
	if (a["level-3"]>0) sel (this);
	//alert (a["id-0"]);
	url (__(this,"vs"), u[0], u[1], a["id-0"]);
}

function _ndr ()
{
        var u = this.id.split ("-");
        var p = __(this).previousSibling;
        var r_ = ra[u[1]][0].slice(0); // get a copy
        rargs (r_, this.nextSibling.childNodes);
        console.log ("[ndr_] "+u[0]+" "+u[1]+" | "+JSON.stringify (r_));
        nd (p, te[u[0]], [], r_, [0]);
}


