var picture_url = "";
var picture_id_temp = "";


$(document).on('pageinit', '#tasks_page_id', function(){
    
    $("#fileupload").fileupload({
        dataType: 'json',
        url: 'http://localhost:8100/social/api/upload-pictures/',
        formData: [{name:"username", value:localStorage.getItem('username')}],
        done: function(e, data){
            console.log(data);
           if(data.result.status == true){
               picture_url = 'http://localhost:8100'+data.result.picture_url
               console.log(picture_url);
               picture_id_temp = data.result.picture_id;
               myNavigator.pushPage('new_photo_view.html');
           }
           else{
               Materialize.toast('Sorry Something Went Wrong Try Again!', 4000);
                console.log("outstanding!");
           }
            
        }
    });
    console.log("initialize upload");
});

function returnTodaysGoals() {
    console.log(picture_id_temp);
    $("#picture_in_need_of_tag").attr('value', picture_id_temp);
    $("#pic_in_need_of_tag img").attr("src", picture_url);
    $("#pic_in_need_of_tag img").attr("style", "width40%;height:40%");
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
                var todaysTasks = statusParse["tasks"];
                //console.log(todaysTasks);
                //console.log(upcomingTask.name_of_task);
                var options = $("#pictures_tasks_list").get(0).options;
                $.each(todaysTasks, function(key, value) {
                    options[options.length] = new Option(value.name_of_task, value.id);
                });
                console.log(todaysTasks);
            }
        },
        });
}

$(document).on('pageinit', '#new_photo_view', function(){
    returnTodaysGoals();
});

function TagPicturetoTasks(){
    var tasksID = $("#pictures_tasks_list").val();
    console.log(tasksID);
    if(tasksID){
        var pictureID = $("#picture_in_need_of_tag").val();
        var task_info = {username:localStorage.getItem('username'), task_id:tasksID, pic_id:pictureID};
        setUpAjax();
        $.ajax({
        url: 'http://localhost:8100/social/api/add-new-pic-to-task',
        type: "POST",
        data: task_info,
        success: function(e){
            console.log(e);
            var statusParse = JSON.parse(e)
            var successStatus = statusParse["status"];
            console.log(successStatus);
            if(successStatus === true){
                 Materialize.toast('Succeded!', 4000);
                myNavigator.popPage();
            }
            else{
                Materialize.toast('Sorry Something Went Wrong Try Again!', 4000);
                console.log("outstanding!");
            }
        },
        });
    }
}