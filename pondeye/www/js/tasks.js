
var TASKS_REMINDER = false;
var reminder_list = [];

$(document).on('pageinit', '#tasks_page_id', function(){
    localStorage.setItem("username", "starken");
    //localStorage.setItem("username", "Uzzis");
   showTasksInfo();
   
  $("#upload_pic").fileupload({
        dataType: 'json',
        url: 'http://localhost:8100/api/upload-picture/',
        done: function(e, data){
            $.each(data.result.files, function(index, file){
                $('<p/>').text(file.name).appendTo(document.body);
                console.log("Uploaded files");
            });
            console.log("the e" + e, " the data" + data);
        }
    });

    console.log("say something giving up on you");
    
     $('.button-collapse').sideNav({// Default is 240
      edge: 'right', // Choose the horizontal origin
      closeOnClick: true // Closes side-nav on <a> clicks, useful for Angular/Meteor
    }
  );
  if(TASKS_REMINDER){
        myNavigator.pushPage('tasks_reminders.html');
        console.log("tasks reminder");
    }
    showReminderOverhead()
});

$(document).on('pageinit', '#tasks_create_form_id', function(){
    if(TASKS_REMINDER){
       // myNavigator.pushPage('tasks_reminders.html');
    }
    showReminderOverhead();
    /*
     $('.button-collapse').sideNav({ // Default is 240
      edge: 'right', // Choose the horizontal origin
      closeOnClick: true // Closes side-nav on <a> clicks, useful for Angular/Meteor
    }
  );
  */
});
$(document).on('pageinit', '#tasks_reminder_page_id', function(){
    console.log(reminder_list);
    showUnDatedTasks(reminder_list);
});


function newUser(){
    console.log(myNavigator.topPage.data);
    console.log("lets do that");
}
function openCalendar(){
    alert("not working");
    //var ref =  cordova.InAppBrowser.open('http://127.0.0.1:8100/calendar/', '_blank', 'location=no');
    var ref =  cordova.InAppBrowser.open('https://www.google.com', '_blank', 'location=no');
} 

function createTask() {
    var new_task_input = $("#new_task_input").val();
    var start_time = $("#new_task_start_time").val();
    var end_time = $("#new_task_end_time").val();
    var new_project_name = $("#new_task_new_project_name").val();
    var existing_project = $("#new_task_existing_project").val();
    var task_info = {username:localStorage.getItem('username'), to_do_item:new_task_input, start_time:start_time, end_time:end_time, new_project:new_project_name,
        existing_project:existing_project, get_what:"create"}
        console.log(end_time);
    if(new_task_input){
        setUpAjax();
        $.ajax({
        url: 'http://localhost:8100/tasks/api/tasks',
        type: "POST",
        data: task_info,
        success: function(e){
            console.log(e);
            var statusParse = JSON.parse(e)
            var successStatus = statusParse["success"];
            console.log(successStatus);
            if(successStatus === "true"){
                myNavigator.popPage(); 
                showTasksInfo()        
            }
            else{
                $("#loginError").show(2000);
                console.log(successStatus); 
            }
        },
    })
  }
}

function updateTask(update_id) {
    var new_task_input = $("#new_task_input-update").val();
    var start_time = $("#update_task_start_time-update").val();
    if(start_time){
        $("#div-task-update-view"+update_id).hide();
    }
    console.log(" start time "+ start_time);
    var end_time = $("#new_task_end_time-update").val();
    var new_project_name = $("#new_task_new_project_name-update").val();
    var existing_project = $("#new_task_existing_project-update").val();
    var task_info = {username:localStorage.getItem('username'), to_do_item:new_task_input, start_time:start_time, end_time:end_time, new_project:new_project_name,
        existing_project:existing_project, get_what:"update", update_id:update_id}
        console.log(end_time);
    if(new_task_input){
        setUpAjax();
        $.ajax({
        url: 'http://localhost:8100/tasks/api/tasks',
        type: "POST",
        data: task_info,
        success: function(e){
            console.log(e);
            var statusParse = JSON.parse(e)
            var successStatus = statusParse["success"];
            console.log(successStatus);
            if(successStatus === "true"){
                myNavigator.popPage(); 
                showTasksInfo()        
            }
            else{
                $("#loginError").show(2000);
                console.log(successStatus); 
            }
        },
    })
  }
}

function showNewTaskOption(){
    $("#show_new_task_options").show(500);
}

function getNewTaskView(){
    // get project options

    var task_info = {username:localStorage.getItem('username'), get_what:"project"};
    setUpAjax();
        $.ajax({
        url: 'http://localhost:8100/tasks/api/tasks',
        type: "GET",
        data: task_info,
        success: function(e){
            console.log(e);
            var statusParse = JSON.parse(e)
            var successStatus = statusParse["status"];
            console.log(successStatus);
            if(successStatus === "true"){
                var project = statusParse["users_project"];
                console.log($('#new_task_existing_project').val());
                var options = $('#new_task_existing_project').get(0).options;
                $.each(project, function(key, value) {
                    options[options.length] = new Option(value, value);
                });
                console.log(project);
                //myNavigator.pushPage('new_task_form.html');         
            }
            else{
                $("#loginError").show(2000);
                console.log(successStatus); 
            }
        },
                error: function(xhr){
                $("#error-message").text(xhr.responseText).show();
                console.log(xhr);
        }  
    });
     $("#show_new_task_options").show(500);
}


function getUpdateTaskView(){
    var task_info = {username:localStorage.getItem('username'), get_what:"project"};
    setUpAjax();
        $.ajax({
        url: 'http://localhost:8100/tasks/api/tasks',
        type: "GET",
        data: task_info,
        success: function(e){
            console.log(e);
            var statusParse = JSON.parse(e)
            var successStatus = statusParse["status"];
            console.log(successStatus);
            if(successStatus === "true"){
                var project = statusParse["users_project"];
                console.log($('#new_task_existing_project-update').val());
                var options = $('#new_task_existing_project-update').get(0).options;
                $.each(project, function(key, value) {
                    options[options.length] = new Option(value, value);
                });
                console.log(project);
                 //myNavigator.pushPage('new_task_form.html');         
            }
            else{
                $("#loginError").show(2000);
                console.log(successStatus); 
            }
        },
                error: function(xhr){
                $("#error-message-update").text(xhr.responseText).show();
                console.log(xhr);
        }  
    });
     $("#show_new_task_options-update").show(500);
}


function individualTaskView(task_id, view){
    var task_info = {username:localStorage.getItem('username'), id:task_id};
    setUpAjax();
        $.ajax({
        url: 'http://localhost:8100/tasks/api/individual-view',
        type: "GET",
        data: task_info,
        success: function(e){
            console.log(e);
            var statusParse = JSON.parse(e)
            console.log(statusParse);
            var successStatus = statusParse["status"];
            console.log(successStatus);
            if(successStatus == true){
                var project = statusParse["project"];
                var task_name = statusParse["task_name"];
                var picture_urls = statusParse["picture_urls"];
                var vouch = statusParse["vouch"];
                var seen = statusParse["seen"];
                var follow = statusParse["follow"];
                var build_cred = statusParse["build_cred"];
                var letDown = statusParse["letDown"];
                $("#modal-tasks-title-"+view).text(task_name);
                console.log("baby should show" + project);
                $('#carousel-task-id-'+view).empty();
                $("#carousel-tasks-pic-id-"+view).empty();
                $("#ind-view-details-"+view).empty();
                $("#ind-goal-view-"+view).empty();
                if(vouch === 0 && build_cred === 0){
                    $("#ind-view-details-"+view).append('<div class="col-md-4">vouches <i class="material-icons">thumb_up</i>'+ vouch+'</div> \
                        <div class="col-md-4"><i class="material-icons">visibility</i> views '+ seen+'</div>');
                }
                else if(build_cred >= 0 && letDown === 0){
                    $("#ind-view-details-"+view).append('<div class="col-md-4">built credibility"'+ build_cred+'"</div>');
                        
                }
                else{
                    $("#ind-view-details-"+view).append('<div class="col-md-4">let downs<i class="material-icons">thumb_down</i>'+ letDown+'</div>');
                }
                if(project){
                    $("#ind-goal-view-"+view).append('<div class=""><p style="white-space:normal;">part of '+ project+' being followed by '+follow+' friends</p></div>');
                }
               

                for(var item = 0; item < picture_urls.length; item++){
                    if(item == 0){
                        $("#carousel-task-id-"+view).append('<li data-target ="#carousel-slider-'+view+'" data-slide-to = "'+item+'" class = "active"></li>');
                        var ind_url = 'http://localhost:8100'+picture_urls[item];
                        $("#carousel-tasks-pic-id-"+view).append('<div class="item active"><img src = "'+ind_url+'" alt = "First slide"></div>');
                    }
                    else{
                        $("#carousel-task-id-"+view).append('<li data-target ="#carousel-slider-'+view+'" data-slide-to = "'+item+'"></li>');
                        var ind_url = 'http://localhost:8100'+picture_urls[item];
                        $("#carousel-tasks-pic-id-"+view).append('<div class="item"><img src = "'+ind_url+'" alt = "'+item +'slide"></div>');
                    }    
                }
                //myNavigator.pushPage('new_task_form.html');         
            }
            else{
                $("#loginError").show(2000);
                console.log("craps" + successStatus); 
            }
        },
                error: function(xhr){
                $("#error-message").text(xhr.responseText).show();
                console.log(xhr);
        }  
    });
}


function showTasksInfo(){
    
    var task_info = {username:localStorage.getItem('username'), get_what:"tasks_info"};
        setUpAjax();
        $.ajax({
        url: 'http://localhost:8100/tasks/api/tasks',
        type: "GET",
        data: task_info,
        success: function(e){
            var statusParse = JSON.parse(e)
            var successStatus = statusParse["status"];
            console.log(successStatus);
            if(successStatus === "true"){
                var upcomingTask = statusParse["upcoming_task"];
                var todaysTasks = statusParse["tasks"];
                var expiredTasks = statusParse["exp_task"];
                var reminders = statusParse["tasks_reminders"];
                var reminder_list_non_alert = statusParse["tasks_reminders_non_alert"];
                if(reminders.length > 0){
                    TASKS_REMINDER = true;
                    reminder_list = reminders;
                    myNavigator.pushPage('tasks_reminders.html');
                    
                    console.log(reminders);
                }
                else if(reminder_list_non_alert){
                    reminder_list = reminder_list_non_alert;
                   
                }
                else{
                    reminder_list = []; 
                    console.log("push me");
                    console.log(reminder_list);
                }
                // reminder_list = reminder_list_non_alert;
                //console.log(todaysTasks);
                //console.log(upcomingTask.name_of_task);
                $("#todays_list").empty();
                $("#expired_task_list").empty();
                if(upcomingTask){
                    setUpcomingTasks(upcomingTask.name_of_task, upcomingTask.start_time, upcomingTask.end_time);
                }
                else{
                    $("#todays_task_span").hide();
                    $("#upcoming_task").empty();
                    $("#upcoming_task").append("<div class='row'>no upcoming tasks</div>");
                }

                for(var index=0; index < todaysTasks.length; index++){
                    
                    var task = todaysTasks[index].name_of_task + " "+todaysTasks[index].start+ " " +todaysTasks[index].end;
                    var task_id = todaysTasks[index].id;
                    var view = 'task-home';
                    $("#todays_list").append('<li><button type="button" class="btn-link" onclick="showTaskModal('+task_id+', \''+view+'\')"><small>'+task+'</small></button></li>');

                }

                if(expiredTasks.length > 0){
                    console.log("expire tasks");
                    for(var index=0; index < expiredTasks.length; index++){
                        
                        var task = expiredTasks[index].name_of_task + " "+expiredTasks[index].start+ " " +expiredTasks[index].end;
                        $("#expired_task_list").append('<ol><li id="exp'+expiredTasks[index].pk+'"><div class="col-md-12"><small>'+task+'</small> \
                        </div><div class="row"><div class="col-md-3"> \
                        <button class="waves-effect waves-light btn" onclick=taskDone('+expiredTasks[index].pk+')>done</button></div><div class="col-md-3"><button \
                        class="waves-effect waves-light btn" onclick=taskFailed('+expiredTasks[index].pk+')>failed</button></div></div></li></ol>');
                    }
                 }
                 else{
                    $("#expired_task_list").append("<small>All taking care off</small>");
                 }
                
                
                /*
                var options = $('#new_task_existing_project').get(0).options;
                $.each(project, function(key, value) {
                    options[options.length] = new Option(value, value);
                });
                
                console.log(project);
                */
                //myNavigator.pushPage('new_task_form.html');         
            }
            else{
                $("#loginError").show(2000);
                console.log(successStatus); 
            }
        },
                error: function(xhr){
                $("#error-message").text(xhr.responseText).show();
                console.log(xhr);
        }  
    });

}

function showTaskModal(task_id, view){
    individualTaskView(task_id, view);
    $("#task_view_modal-"+view).modal();
}

function showUpdateTask(task_id, task_name){
    
    myNavigator.pushPage('new_update_form.html');  
    $(document).on('pageinit', '#tasks_update_form_id', function(){
        $("#new_task_input-update").text(task_name);
        $("#update_view_button").empty();
        $("#update_view_button").append('<a onclick="updateTask('+task_id+')" class="waves-effect waves-light btn">Update Tasks</a>');  
    });
}

function showUnDatedTasks(tasks){
    $("#tasks-reminders").empty();
    if(tasks.length > 0){
        for(var i = 0; i < tasks.length; i++){
            var task_id = tasks[i].id;
            var task = tasks[i].name_of_task;
            $("#tasks-reminders").append('<div class="row" id="div-task-update-view'+task_id+'"><div class="col-md-3"><li><button type="button" class="btn-link" \
            onclick="showUpdateTask('+task_id+', \''+task+'\')"><span>'+task+'</span></button></li></div></div>'); 
        }
    }
    else{
        $("#tasks-reminders_done").show();
    }

    TASKS_REMINDER = false;
}

function showReminderOverhead(){
    if(TASKS_REMINDER){
        $("#show-reminder-").show();
    }
    else{
        $("#show-reminder-").hide();
    }
}
function taskDone(pk){
    var task_info = {username:localStorage.getItem('username'), pk:pk};
   setUpAjax(); 
   $.ajax({
        url: 'http://localhost:8100/tasks/api/task-done-check-off/',
        type: "POST",
        data: task_info,
        success: function(result){
        var resultParse = JSON.parse(result)
        var successStatus = resultParse["status"];
        if(successStatus === true){
            $("#exp"+pk).hide();
            console.log("successfull failed tasks");
        }
     },
      error: function(xhr){
            $("#error-message").text(xhr.responseText).show();
            console.log(xhr);
      }
    });
}

function taskFailed(pk){
    var task_info = {username:localStorage.getItem('username'), pk:pk};
   setUpAjax(); 
   $.ajax({
        url: 'http://localhost:8100/tasks/api/task-failed-check-off/',
        type: "POST",
        data: task_info,
        success: function(result){
        var resultParse = JSON.parse(result)
        var successStatus = resultParse["status"];
        if(successStatus === true){
            $("#exp"+pk).hide();
            console.log("successfull failed tasks");
        }
     },
      error: function(xhr){
            $("#error-message").text(xhr.responseText).show();
            console.log(xhr);
      }
    });
}

function setUpcomingTasks(name_of_task, start_time, end_time){
        $("#upcoming_task").empty();
        $("#current_to_do").text(name_of_task);
        console.log(name_of_task);
        $("#start_time_todo").text(start_time);
        $("#end_time_todo").text(end_time);
}
function showTodaysTasks(){
    $("#todays_list").toggle(500);
}
function toggleNav(){
    console.log("do something"); 
    // Show sideNav
       
}
