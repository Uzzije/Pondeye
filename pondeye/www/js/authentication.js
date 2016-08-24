//ons.ready(function(){
function setUpAjax(){ 
        var crsftoken = Cookies.get('csrftoken');  
        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", crsftoken);
                    console.log("cross down "+ crsftoken);
                   }
                   console.log("cross up! "+ crsftoken);
                }
        });
}

function startSession(){
        setUpAjax();
        user_info = {username:localStorage.getItem("username"), password:localStorage.getItem("password")};
        $.ajax({
        url: 'http://localhost:8100/tasks/api/start_session',
        type: "GET",
        data: user_info,
        success: function(e){
            console.log(e);
            var statusParse = JSON.parse(e)
            var successStatus = statusParse["authenticate"];
            console.log(successStatus);
            if(successStatus === "false"){
                myNavigator.pushPage("login.html");
                         
            }
            else{
                myNavigator.pushPage("tasks_view.html");
                //showTasksInfo(); 
                
            }
        },
        error: function(xhr){
            $("#error-message").text(xhr.responseText).show();
            console.log(xhr);
        }  
    });
}

function login()
{
    console.log("i stopped");
    var username = $(".userName").val();
    var password = $(".userPassword").val();
    console.log(username + " "+password);
     setUpAjax();
    user_info = {username:username, password:password};
    $.ajax({
        url: 'http://localhost:8100/tasks/api/login',
        type: "GET",
        data: user_info,
        success: function(e){
            console.log(e);
            var statusParse = JSON.parse(e)
            var successStatus = statusParse["success"];
            console.log(successStatus);
            if(successStatus === "true"){
                localStorage.setItem("username", username);
                localStorage.setItem("password", password);
                myNavigator.pushPage("tasks_view.html");
                
            }
            else{
                $("#loginError").show(2000);
                console.log("Now errors"); 
            }
        },
                error: function(xhr){
                $("#error-message").text(xhr.responseText).show();
        }  
    })
}    

function signUp(){
    var username = $("#username_reg").val();
    var password = $("#password_reg_one").val();
    var conf_password = $("#password_reg_two").val();
    var email = $("#email_reg").val();
    var first_name = $("#first_name_reg").val();
    var last_name = $("#last_name_reg").val();
    var error_message;
    if(username === ''){
        $("#userNameError").show(1000);
    }
    else{
        $("#userNameError").hide(1000);
    }
    if(password === '' || conf_password === '' && password !== conf_password){
        $("#passwordError").show(1000);
    }
    else{
        $("#passwordError").hide(1000);
    }
    if(emailIsValid(email) === false){
        $("#emailError").show(1000);
    }
    else{
        $("#emailError").hide(1000);
    }
    if(first_name === ''){
        $("#firstNameError").show(1000);
    }
    else{
        $("#firstNameError").hide(1000);
    }
    if(last_name === ''){
        $("#lastNameError").show(1000);
    }
    else{
        $("#lastNameError").hide(1000);
    }
    if(last_name && username && password && conf_password && emailIsValid(email) && first_name && last_name){
        setUpAjax();
        
        user_info = { 'user_name':username, 'password':password, 'email':email, 'first_name':first_name, 'last_name':last_name};
        
        $.ajax({
            url: 'http://localhost:8100/tasks/api/register/',
            type: "POST",
            crossDomain: true,
            data: user_info,
            success: function(e){
                console.log(e);
                var statusParse = JSON.parse(e)
                var successStatus = statusParse["success"];
                console.log(successStatus);
                var message_answer = 'Thanks for signing up '+first_name+'!';
                if(successStatus === "created"){
                    console.log("created!!");
                    localStorage.setItem("username", username);
                    myNavigator.pushPage("add_new_task.html", {data:
                        {welcome_message: 
                        message_answer}})   
                }
                else{
                    $("#registerEntryErrorMessage").text(successStatus)
                    $("#registerEntryError").show(2000);
                    console.log(successStatus); 
                }
            },
                error: function(xhr){
                $("#error-message").text(xhr.responseText).show();
                console.log(xhr.responseText);
          }  
        })
    }
}

function emailIsValid(email){
    if(email && email.indexOf('@') > -1 && (email.indexOf('@') === email.lastIndexOf('@')) 
        && (email.indexOf('.') > email.indexOf('@'))){
            return true;
    }
    else{
        return false
    }
}
//});