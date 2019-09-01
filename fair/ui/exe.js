
function get_post_type(){
    var type = $("input[name='post_type']:checked").val();
    type = type ? type : post_type;
    return type ? type : 'j';
}
$(document).ready(function(){
    $('#head .url').text(window.location.pathname);
    $('.method-chooser').dropdown({
        on: 'hover'
    });
    $('.method-chooser div.item').on('click', function() {
        var api = $(this)[0].innerText.split(" ");
        url = window.location.pathname + '?type=' + get_post_type() + '&api=' + api[0] + '&method=' + api[1];
        console.log(url);
        $('.method-chooser span.method-name').text(api[0]);
        // window.location.href =
    });
    init_test_case();
    $('.param-mode').change(function(){
        if($('.param-mode').is(':checked')){
            $("input[name='param_select']").prop("checked", true);
            $("input[name='param_select']").attr('disabled', 'disabled');
        } else {
            $("input[name='param_select']").removeAttr('disabled');
            $("input[name='param']").each(function(){
                if (this.value) {
                    $("#" + this.id + "_select").prop("checked", true);
                } else {
                    $("#" + this.id + "_select").prop("checked", false);
                }
            });
        }
    });
    if ($('#body .params').height() > $('#body .use-case').height()) {
        $('#body .use-case').height($('#body .params').height());
    }
    if (window.innerHeight > 480) {
        $('#result').height(window.innerHeight - 200);
    }

    $(".has-hint").mouseover(function(){
        $("#head .hint-info span").html($(this).attr('hint'));
    });
    $(".has-hint").mouseout(function(){
        $(".menu .hint-info span").html('');
    });

    $(".green.ok.button").click(save_config);
});

function url_to_json(url) {
    if (url === '')
        return '';
    var pairs = (url || location.search).slice(1).split('&');
    var result = {};
    for (var idx in pairs) {
        var pair = pairs[idx].split('=');
        if (!!pair[0])
            result[pair[0]] = decodeURIComponent(pair[1] || '');
    }
    return result;
}

function param_onchange(param){
    if(!$('.param-mode').is(':checked')) {
        if (param.value) {
            $("#" + param.id + "_select").prop("checked", true);
        } else {
            $("#" + param.id + "_select").prop("checked", false);
        }
    }
}

function get_params(auto_gen_param){
    var params = {};
    $("input[name='param']").each(function(){
        var id = this.id;
        var value = '';
        var gen_url = $("#" + this.id + "_url").val();
        if (gen_url.split('[').length == 2 && gen_url.split(']').length == 2) {
            var _name = gen_url.split('[')[1].split(']')[0];
            var gen_url = gen_url.split('[')[0] + $('#' + _name).val() + gen_url.split(']')[1];
        }
        var pure_auto = $("#" + this.id + "_pure_auto").is(':checked');
        // pure-automatic generate (Input Value is not need)
        if(auto_gen_param && gen_url && pure_auto && !this.value){
            value = $.ajax({
                url: gen_url,
                async: false,
                error: function(xhr, status, error) { alert('parameter [' + id + '] generate fail [' + gen_url + ']');}
            }).responseText;
        }
        if (value || $("#" + this.id + "_select").is(':checked')) {
            if (!value) {
                // semi-automatic generate (Input Value is need)
                if(!pure_auto && auto_gen_param && gen_url){
                    var tv = this.value;
                    value = $.ajax({
                        url: gen_url + this.value,
                        async: false,
                        error: function(xhr, status, error) { alert('parameter [' + id + '] generator fail [' + gen_url + tv + ']');}
                    }).responseText;
                } else {
                    value = this.value;
                }
            }
            var type = $("#" + this.id + "_type").val();
            console.log(type);
            if (type == 'Int' || type == 'Float') {
                if (value) {
                    var _value = new Number(value);
                    params[this.id] = isNaN(_value) ? value : _value;
                } else {
                    params[this.id] = null;
                }
            } else if (type == 'Bool'){
                if (value == 'true' || value == 'True') {

                }

            } else if (type.substr(0, 5) == 'List[') {
                if ($.trim(value)) {
                    params[this.id] = [];
                    var _type = type.substr(5, type.length - 6);
                    var _param = $.trim(value).split(',');
                    for (var index = 0; index < _param.length; index++) {
                        if (_type == 'Int' || _type == 'Float') {
                            if ($.trim(_param[index])) {
                                var _value = new Number(_param[index]);
                                params[this.id].push(isNaN(_value) ? _param[index] : _value);
                            } else {
                                params[this.id].push(null);
                            }
                        } else {
                            params[this.id].push(_param[index]);
                        }
                    }
                }
            } else {
                params[this.id] = value;
            }
        }
    });
    return params;
}

function do_use_json(){
    var json_str = $("#result")[0].value;
    try{
        var params = JSON.parse(json_str);
    }catch(e){
        // convert u（u'' -> "")
        json_str = json_str.replace(new RegExp("u'", "g"), "\"");
        json_str = json_str.replace(new RegExp("'", "g"), "\"");
        try{
            var params = JSON.parse(json_str);
        }catch(e){
            alert('SyntaxError');
            return;
        }
    }
    for (var item in params) {
        if ($("#" + item).length == 0) {
            alert('Unknown parameter [' + item + '], This parameter will cause [param_unknown] abnormal.');
        }
    }
    $("input[name='param']").each(function(){
        if (params.hasOwnProperty(this.id)){
            this.value=params[this.id];
            $("#" + this.id + "_select").prop("checked", true);
        }
    })
}

function do_to_json(){
    var params = get_params(false);
    if(params){
        $("#result")[0].value = JSON.stringify(params, null, 4);
    }
}

function do_use_url(){
    var params_str = $("#result")[0].value;
    if (params_str.substring(0, curr_api_path.length) == curr_api_path) {
        params_str = params_str.substring(curr_api_path.length, params_str.length)
    }
    try {
        var params = url_to_json(params_str);
        for (var item in params) {
            if ($("#" + item).length == 0) {
                alert('Unknown parameter [' + item + '], This parameter will cause [param_unknown] abnormal.');
            }
        }
    }catch(e){
        alert('SyntaxError');
        return;
    }
    $("input[name='param']").each(function(){
        if (params.hasOwnProperty(this.id)){
            this.value=params[this.id];
            $("#" + this.id + "_select").prop("checked", true);
        }
    });
}

function do_to_url(){
    var params = get_params(false);
    if(params){
        $("#result")[0].value = '?' + $.param(params);
    }
}

function execute(){
    var params = get_params(true);
    var params_str = $.param(params);
    if(!params){
        return;
    }
    if (c_method == "GET") {
        var request = {
            type: 'GET',
            url: params_str ? curr_api_path + "?" + params_str : curr_api_path,
            timeout: 30000,
            success: function(_data, textStatus, jqXHR){
                try{
                    $("#result")[0].value = JSON.stringify(_data, null, 4);
                }catch(e){
                    $("#result")[0].value = _data;
                }
                save_case(_data.code);
            },
            error: function(xhr, status, error) { alert('Can not access API [' + curr_api_path + ']'); }
        };
        if ($('#json_p').is(':checked')){
            request.dataType = 'jsonp';
            request.jsonp = curr_api_json_p;
            //request.cache = true;     // Let jquery not use "_" parameter (a timestamp, to prevent the server cache)
        }
        $.ajax(request);
    } else {
        if (get_post_type() == 'j') {
            $.ajax({
                url: curr_api_path,
                type: 'POST',
                data: JSON.stringify(params),
                timeout: 30000,
                dataType: 'json',
                contentType: 'application/json; charset=utf-8',
                success: function(_data, textStatus, jqXHR){
                    try{
                        $("#result")[0].value = JSON.stringify(_data, null, 4);
                    }catch(e){
                        $("#result")[0].value = _data;
                    }
                    save_case(_data.code);
                },
                error: function(xhr, status, error) { alert('Can not access API [' + curr_api_path + ']'); }
            });
        } else {
            var is_json = true;
            $("input[name='param']").each(function() {
                var type = $("#" + this.id + "_type").val();
                if (type.substr(0, 5) == 'List[') {
                    alert('application/x-www-form-urlencoded not support List parameter, Please use application/json.')
                    is_json = false;
                    return;
                }
            });
            if (!is_json) { return; }
            $.ajax({
                url: curr_api_path,
                type: 'POST',
                data: params,
                dataType: 'json',
                timeout: 30000,
                success: function(_data, textStatus, jqXHR){
                    try{
                        $("#result")[0].value = JSON.stringify(_data, null, 4);
                        save_case(_data.code);
                    }catch(e){
                        $("#result")[0].value = _data;
                    }
                },
                error: function(xhr, status, error) { alert('Can not access API [' + curr_api_path + ']'); }
            });
        }
    }
}

function init_test_case(){
    $(".case .menu .item").each(function(){
        var cases = JSON.parse($(this).attr('cases'));
        test_cases[$(this).html()] = cases;
        if (cases.length != 0){
            $(this).append('<i class="share icon"></i>');
            $(this).attr('use_index', cases.length-1);
        }
    });
}

function params_not_equal(old_params, new_params){
    // while old_params is a subset of new_params
    for (var param in old_params) {
        // toString for list support
        var old_sign = typeof old_params[param] == 'undefined' ? old_params[param] : old_params[param].toString();
        var new_sign = typeof new_params[param] == 'undefined' ? new_params[param] : new_params[param].toString();
        if (old_sign != new_sign){
            return true;
        }
    }
    // while new_params is a subset of old_params
    for (var param in new_params) {
        var old_sign = typeof old_params[param] == 'undefined' ? old_params[param] : old_params[param].toString();
        var new_sign = typeof new_params[param] == 'undefined' ? new_params[param] : new_params[param].toString();
        // toString for list support
        if (old_sign != new_sign){
            return true;
        }
    }
    return false;
}

function save_case(code){
    var param_mode = $('.param-mode').is(':checked');
    var data = {
        "params": get_params(false),
        "param_mode": param_mode,
        "method": c_method,
        "code": code
    };
    $.ajax({
        url: window.location.pathname + '/save_case',
        type: 'POST',
        data: JSON.stringify(data),
        timeout: 30000,
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        success: function(_data, textStatus, jqXHR){
            if (_data.result == 'success'){
                if (test_cases[code].length == 0) {
                    $(".case .menu .item[code='" + code + "']").append('<i class="share icon"></i>');
                }
                var old_cases = test_cases[code];
                test_cases[code] = [];
                for (var i=0; i<old_cases.length; i++) {
                    if (params_not_equal(old_cases[i].params, get_params(false)) || old_cases[i].param_mode!=param_mode){
                        test_cases[code].push({"params": old_cases[i].params,
                                               "param_mode": old_cases[i].param_mode});
                    }
                }
                test_cases[code].push({"params": get_params(false), "param_mode": param_mode});
                test_cases[code] = test_cases[code].slice(-10);
                var use_index = test_cases[code].length - (test_cases[code].length > 1 ? 2 : 1);
                $(".case .menu .item[code='" + code + "']").attr('use_index', use_index);
            } else {
                alert(JSON.stringify(_data, null, 4));
            }
        },
        error: function(xhr, status, error) { alert('Can not access API [' + window.location.pathname + '/tests/save_case]'); }
    });
}

function use_case(code){
    var use_index = $(".case .menu .item[code='" + code + "']").attr('use_index');
    if (use_index == -1){
        return;
    }
    $(".case .menu .item[code='" + code + "']").attr('use_index', use_index==0 ? test_cases[code].length-1 : use_index-1);

    var test_case = test_cases[code][use_index];
    var params = test_case['params'];
    $("input[name='param']").each(function(){
        if (params.hasOwnProperty(this.id)){
            this.value=params[this.id];
            $("#" + this.id + "_select").prop("checked", true);
        } else {
            this.value='';
            $("#" + this.id + "_select").prop("checked", false);
        }
    })
    if (test_case.param_mode){
        $('.param-mode').prop("checked", true);
        $("input[name='param_select']").prop("checked", true);
        $("input[name='param_select']").attr('disabled', 'disabled');
    } else {
        $('.param-mode').prop("checked", false);
        $("input[name='param_select']").removeAttr('disabled');
    }
}

function get_params_config(){
    var params = {};
    $("input[name='param']").each(function(){
        var param = {};
        param.pure_auto = $("#" + this.id + "_pure_auto").is(':checked');
        param.url = $("#" + this.id + "_url").val();
        params[this.id] = param;
    });
    return params;
}

function save_config(){
    var data = {
        "post_type": get_post_type(),
        "json_p": $('#json_p').is(':checked'),
        "method": c_method,
        "params": get_params_config()
    };
    $.ajax({
        url: window.location.pathname + '/save_config',
        type: 'POST',
        data: JSON.stringify(data),
        timeout: 30000,
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        success: function(_data, textStatus, jqXHR){
            if (_data.result != 'success'){
                alert(JSON.stringify(_data, null, 4));
            }
        },
        error: function(xhr, status, error) { alert('Can not access API [' + window.location.pathname + '/tests/save_config]'); }
    });
}

function show_doc(){
    window.location = window.location.pathname + '?fair=doc';
}