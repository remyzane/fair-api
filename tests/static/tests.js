
function get_post_type(){
    var type = $("input[name='post_type']:checked").val();
    type = type ? type : post_type;
    return type ? type : 'j';
}

$(document).ready(function(){
    $('.ui.menu .ui.dropdown').dropdown({
        on: 'hover'
    });
    ZeroClipboard.config( { swfPath: "/res/libs/ZeroClipboard.swf" } );
    var client = new ZeroClipboard($(".copy-button"));
    client.on( "copy", function (event) {
        var params = curr_api_method == 'GET' ? $.param(get_params(true)) : null;

        var clipboard = event.clipboardData;
        clipboard.setData( "text/plain", params ? curr_api_path + "?" + params : curr_api_path);
    });

    $('.ui.menu .uri.item').on('click', function() {
        window.location.href = window.location.pathname +
            '?user=' + user + '&type=' + get_post_type() + '&api=' + $(this)[0].innerText;
    });
    $('.body .ui.link.api.items').css({"margin-left": ($(window).width()-800)/2 + "px"});
    $('.body .ui.link.api.items .item').on('click', function() {
        var uri = $(this)[0].children[0].children[0].innerText;
        window.location.href = window.location.pathname +
            '?user=' + user + '&type=' + get_post_type() + '&api=' + uri;
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
    if ($('.body .params').height() > $('.body .use-case').height()) {
        $('.body .use-case').height($('.body .params').height());
    }
    if (window.innerHeight > 480) {
        $('#result').height(window.innerHeight - 180);
    }

    $(".case .item").mouseover(function(){
        $(".case .message span").html($(this).attr('message'));
    });
    $(".case .item").mouseout(function(){
        $(".case .message span").html($(".case .description").html());
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

// 获取参数
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
        // 纯自动生成时(如果用户没输入则自动生成)
        if(auto_gen_param && gen_url && pure_auto && !this.value){
            value = $.ajax({
                url: gen_url,
                async: false,
                error: function(xhr, status, error) { alert('参数【' + id + '】生成失败【' + gen_url + '】');}
            }).responseText;
        }
        if (value || $("#" + this.id + "_select").is(':checked')) {
            if (!value) {
                // 半自动生成时(需要用户输入)
                if(auto_gen_param && gen_url && !pure_auto){
                    var tv = this.value;
                    value = $.ajax({
                        url: gen_url + this.value,
                        async: false,
                        error: function(xhr, status, error) { alert('参数【' + id + '】生成失败【' + gen_url + tv + '】');}
                    }).responseText;
                } else {
                    value = this.value;
                }
            }
            var type = $("#" + this.id + "_type").val();
            if (type == 'Int' || type == 'Float') {
                if (value) {
                    var _value = new Number(value);
                    params[this.id] = isNaN(_value) ? value : _value;
                } else {
                    params[this.id] = null;
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
        // 转换 u（u'' -> "")
        json_str = json_str.replace(new RegExp("u'", "g"), "\"");
        json_str = json_str.replace(new RegExp("'", "g"), "\"");
        try{
            var params = JSON.parse(json_str);
        }catch(e){
            alert('SyntaxError');
            return;
        }
    }
    // 检测是否有多余参数
    for (var item in params) {
        if ($("#" + item).length == 0) {
            alert('未知参数【' + item + '】，该参数会引起接口［param_unknown］异常');
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
    // 获取参数
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
        // 检测是否有多余参数
        for (var item in params) {
            if ($("#" + item).length == 0) {
                alert('未知参数【' + item + '】，该参数会引起接口［param_unknown］异常');
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
    // 获取参数
    var params = get_params(false);
    if(params){
        $("#result")[0].value = '?' + $.param(params);
    }
}

function do_test(){
    // 获取参数
    var params = get_params(true);
    var params_str = $.param(params);
    if(!params){
        return;
    }
    if (curr_api_method == "GET") {
        var request = {
            type: 'GET',
            url: params_str ? curr_api_path + "?" + params_str : curr_api_path,
            timeout: 30000,
            success: function(_data, textStatus, jqXHR){
                try{
                    $("#result")[0].value = JSON.stringify(_data, null, 4);
                    save_case(_data.code);
                }catch(e){
                    $("#result")[0].value = _data;
                }
            },
            error: function(xhr, status, error) { alert('接口【' + curr_api_path + '】无法访问'); }
        };
        if ($('#json_p').is(':checked')){
            request.dataType = 'jsonp';
            request.jsonp = json_p;
            request.cache = true;           // 避免jquery自动加上"_"参数(一个时间戳, 用户防止服务器端缓存)
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
                        save_case(_data.code);
                    }catch(e){
                        $("#result")[0].value = _data;
                    }
                },
                error: function(xhr, status, error) { alert('接口【' + curr_api_path + '】无法访问');}
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
                error: function(xhr, status, error) { alert('接口【' + curr_api_path + '】无法访问');}
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

// old_params 和 new_params 属性可能是子集关系,所以需要两轮判断
function params_not_equal(old_params, new_params){
    for (var param in old_params) {
        // 加toString是为了判断能够兼容数组
        var old_sign = typeof old_params[param] == 'undefined' ? old_params[param] : old_params[param].toString();
        var new_sign = typeof new_params[param] == 'undefined' ? new_params[param] : new_params[param].toString();
        if (old_sign != new_sign){
            return true;
        }
    }
    for (var param in new_params) {
        var old_sign = typeof old_params[param] == 'undefined' ? old_params[param] : old_params[param].toString();
        var new_sign = typeof new_params[param] == 'undefined' ? new_params[param] : new_params[param].toString();
        // 加toString是为了判断能够兼容数组
        if (old_sign != new_sign){
            return true;
        }
    }
    return false;
}

function save_case(code){
    var param_mode = $('.param-mode').is(':checked');
    var data = {
        "user": user,
        "api_path": curr_api_uri,
        "params": get_params(false),
        "param_mode": param_mode,
        "code": code,
    };
    $.ajax({
        url: '/tests/save_case/',
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
        error: function(xhr, status, error) { alert('接口【/tests/save_case/】无法访问');}
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

// 获取参数配置
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
        "user": user,
        "api_path": curr_api_uri,
        "post_type": get_post_type(),
        "json_p": $('#json_p').is(':checked'),
        "params": get_params_config()
    };
    $.ajax({
        url: '/tests/save_config/',
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
        error: function(xhr, status, error) { alert('接口【/tests/save_config/】无法访问');}
    });
}
