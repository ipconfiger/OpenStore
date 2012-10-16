/**
 * Created with PyCharm.
 * User: alex
 * Date: 12-9-25
 * Time: 下午10:53
 * To change this template use File | Settings | File Templates.
 */

function pop_alert(type,message){
    $("#alert_bar").html("");
    $("#alert_bar").show('slow');
    if (type=="info"){
        $("#alert_bar").html("<div class=\"alert\">"+message+"<a href=\"#\" class=\"close\" data-dismiss=\"alert\">×</a></div>");
    }
    if (type=="err"){
        $("#alert_bar").html("<div class=\"alert alert-error\">"+message+"<a href=\"#\" class=\"close\" data-dismiss=\"alert\">×</a></div>");
    }
    $(".alert").alert();
    setTimeout(function(){
        $("#alert_bar").hide("slow");
        $("#alert_bar").html("");
    },5000);
}