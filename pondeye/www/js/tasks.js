
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
        existing_project:existing_project}
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

function showTasksInfo(){
    
    var task_info = {username:localStorage.getItem('username'), get_what:"tasks_info"};
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
                var upcomingTask = statusParse["upcoming_task"];
                var todaysTasks = statusParse["tasks"];
                var expiredTasks = statusParse["exp_task"]
                //console.log(todaysTasks);
                //console.log(upcomingTask.name_of_task);
                setUpcomingTasks(upcomingTask.name_of_task, upcomingTask.start_time, upcomingTask.end_time);
                 $("#todays_list").empty();
                 $("#expired_task_list").empty();
                for(var index=0; index < todaysTasks.length; index++){
                    var task = todaysTasks[index].name_of_task + " "+todaysTasks[index].start+ " " +todaysTasks[index].end;
                    $("#todays_list").append('<li><small>'+task+'</small></li>');
                }
                for(var index=0; index < expiredTasks.length; index++){
                    var task = expiredTasks[index].name_of_task + " "+expiredTasks[index].start+ " " +expiredTasks[index].end;
                    $("#expired_task_list").append('<li><div class="col-md-6><small>'+task+'</small></div><div class="col-md-3><button \
                    onclick=taskDone('+expiredTasks[index].pk+')>done</button></div><div class="col-md-3><button \
                    onclick=taskFailed('+expiredTasks[index].pk+')>failed</button></div></li>');
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
function setUpcomingTasks(name_of_task, start_time, end_time){
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
$(document).on('pageinit', '#tasks_page_id', function(){
   showTasksInfo();
   
    $('.button-collapse').sideNav({// Default is 240
      edge: 'right', // Choose the horizontal origin
      closeOnClick: true // Closes side-nav on <a> clicks, useful for Angular/Meteor
    }
  );
  
});
$(document).on('pageinit', '#tasks_create_form_id', function(){
    /*
     $('.button-collapse').sideNav({ // Default is 240
      edge: 'right', // Choose the horizontal origin
      closeOnClick: true // Closes side-nav on <a> clicks, useful for Angular/Meteor
    }
  );
  */
});