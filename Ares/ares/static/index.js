function init_csrf_token(){
    $(document).ajaxSend(function(event, xhr, settings) {
            function getCookie(name) {
                    var cookieValue = null;
                    if (document.cookie && document.cookie !== '') {
                            var cookies = document.cookie.split(';');
                            for (var i = 0; i < cookies.length; i++) {
                                    var cookie = jQuery.trim(cookies[i]);
                                    // Does this cookie string begin with the name we want?
                                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                            break;
                                    }
                            }
                    }
                    return cookieValue;
            }
            function sameOrigin(url) {
                    // url could be relative or scheme relative or absolute
                    var host = document.location.host; // host + port
                    var protocol = document.location.protocol;
                    var sr_origin = '//' + host;
                    var origin = protocol + sr_origin;
                    // Allow absolute or scheme relative URLs to same origin
                    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                            // or any other URL that isn't scheme relative or absolute i.e relative.
                            !(/^(\/\/|http:|https:).*/.test(url));
            }
            function safeMethod(method) {
                    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
            }

            if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }

    });
}

function setup(){


    $('body').layout({
        defaults: {
            applyDefaultStyles: true,
            slidable: false,
            togglerLength_closed: -1
        },
        east: {
            size: 400
        },
        west: {
            size: 200
        }
    });
    $('#east').layout({
        defaults: {
            applyDefaultStyles: true,
            slidable: false,
            togglerLength_closed: -1
        },
        north: {
            size: 200
        }
    });


    $('#files').on("change", "input[name=file]",function(){
        clicked = $(this).val();
        if(clicked){
            $.get('./' + clicked + '/', function(data){
                editor.setValue(data);
            });
        }

    });


    setInterval(function(){

        opened = $('input[name=file]:checked', '#files').val();
        if(opened){
            $.post('./' + opened + '/ding').error(function(){
                alert('Something is awry, proceed with caution. This may be the result of lag, or having the same document open in multiple tabs/windows');
            });
        }
        $('.status').each(function(){
            file = this.id.split('-')[1];
            var cur = $(this);
            $.get('./' + file + '/status', function(data){
                cur.removeClass (function (index, css) {
                    return (css.match (/ui-icon-\S+/g) || []).join(' ');
                });
                cur.addClass(data);
            });
        });
    }, 2000);


    $('#test').click(function(e){
        e.preventDefault();
        $('#results').html('<p style="width:100%; text-align:center">running<br/><img src="static/spin.gif" /></p>');
        $.post('index.html', {'cmd': editor.getValue(), 'input': $('#input').val()}, function(data, textstatus, jqXHR){
            $('#results').html(data);
        });
    });
}