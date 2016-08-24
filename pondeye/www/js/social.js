var globalSearchWord = '';
$(document).on('pageinit', '#social_feed_id', function(){
    console.log("i am being called!");
    getNewsFeed();
    
});
$(document).on('pageinit', '#search_view_id', function(){
    console.log("i am being searched!");
    findPeople(globalSearchWord);
    
});
$(document).on('pageinit', '#friendship_view_id', function(){
    console.log("i am being searched!");
    getFriendShipRequest();
});

function getNewsFeed(){
    
        var feed_info = {username:localStorage.getItem('username'), get_what:"user_feed"};
        setUpAjax();
        $.ajax({
        url: 'http://localhost:8100/social/api/newsfeed',
        type: "GET",
        data: feed_info,
        success: function(result){
            console.log(result);
            var statusParse = JSON.parse(result)
            var successStatus = statusParse["status"];
            if(successStatus === "true"){
                var newsFeed = statusParse["feed"];
                var todaysTasks = statusParse["tasks"];
                console.log(newsFeed);
                 $("#feed_body_id").empty();
                for(var index=0; index < newsFeed.length; index++){
                    //create row div
                    $("#feed_body_id").append('<div id="'+newsFeed[index].id+'" class="row panel panel-default"></div>');
                    var nameOfFeedH = $('#'+newsFeed[index].id).append('<small>'+newsFeed[index].name_of_feed+'</small>');
                    if(newsFeed[index].completed || newsFeed[index].task_failed){
                        if(newsFeed[index].completed){
                            //create div build
                            $('#'+newsFeed[index].id).append('<div class="col-md-1"><small>build cred '+newsFeed[index].build_cred_count+'</small></div>');
                        }
                        if(newsFeed[index].failed){
                            //create div letdown
                            $('#'+newsFeed[index].id).append('<div class="col-md-1"><small>let downs '+newsFeed[index].letDown_count+'</small></div>');
                        }  
                    }
                    else{
                        //create vouche count
                        var vouch_id = "vouch"+newsFeed[index].id;
                        $('#'+newsFeed[index].id).append('<div class="col-md-1"><small><a onclick="createVouch('+newsFeed[index].id+')">vouch </a><span id="'+vouch_id+'">'+newsFeed[index].vouche_count+'</span></small></div>');
                    }
                    if(newsFeed[index].partOfProject){
                        //create follow count
                        var project_id = "project" + newsFeed[index].id;
                        $('#'+newsFeed[index].id).append('<div class="col-md-1"><small><a onclick="createFollow('+newsFeed[index].id+')">follows </a> <span id="'+project_id+'">'+newsFeed[index].follow_count+'</span></small></div>');
                    }
                    //create seen count
                    $('#'+newsFeed[index].id).append('<div class="col-md-1"><small>seen '+newsFeed[index].seen_count+'</small></div>');
                }
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

function createVouch(tasks_id){
   var vouch_info = {username:localStorage.getItem('username'), task_id:tasks_id};
   setUpAjax(); 
   console.log("getting heer");
   $.ajax({
        url: 'http://localhost:8100/social/api/create-vouch/',
        type: 'POST',
        data: vouch_info,
        success: function(result){
        var resultParse = JSON.parse(result)
        var successStatus = resultParse["status"];
        if(successStatus === "true"){
            $("#vouch"+tasks_id).text(resultParse["count"]);
        }
   },
    error: function(xhr){
        $("#error-message").text(xhr.responseText).show();
        console.log(xhr);
    }
});
}

function createFollow(task_id){
   var project_info = {username:localStorage.getItem('username'), task_id:task_id};
   setUpAjax(); 
   $.ajax({
        url: 'http://localhost:8100/social/api/create-follow/',
        type: "POST",
        data: project_info,
        success: function(result){
        var resultParse = JSON.parse(result)
        var successStatus = resultParse["status"];
        if(successStatus === "true"){
            $("#project"+task_id).text(resultParse["count"]);

        }
     },
      error: function(xhr){
            $("#error-message").text(xhr.responseText).show();
            console.log(xhr);
      }
    });
}
function findPeople(search_word){
    console.log("finding people");
    var search_info = {username:localStorage.getItem('username'), query_word:search_word};
    setUpAjax(); 
       $.ajax({
        url: 'http://localhost:8100/social/api/social-search/',
        type: "GET",
        data: search_info,
        success: function(result){
        var resultParse = JSON.parse(result)
        console.log(resultParse);
        var successStatus = resultParse["status"];
        $("#search_body_id").empty();
        if(successStatus === true){
            var search_result = resultParse["found_results"];
            console.log("make me miss");
            for(var index=0; index < search_result.length; index++){
                $("#search_body_id").append('<div id='+search_result[index].username+' class="row"></div>');
                var name = search_result[index].first_name + " "+ search_result[index].last_name
                $("#"+search_result[index].username).append('<div class="col-md-3">'+name+'</div>');
                if(search_result[index].are_friends){
                    $("#"+search_result[index].username).append('<div class="col-md-3">friends</div>');
                }
                else{
                    $("#"+search_result[index].username).append('<div class="col-md-3"><button id="add-friend-button" \
                    name="'+search_result[index].id+'" onclick=send_friends_request('+search_result[index].id+') class="btn-link">Add Friend</button></div>');
                }
            }
        }
     },
      error: function(xhr){
            $("#error-message").text(xhr.responseText).show();
            console.log(xhr);
      }
    });
}

function feed_view_search(){
    console.log("submitting field");
    var search_word = $("#feed_search_id").val();
    if(search_word){
        globalSearchWord = search_word;
        myNavigator.pushPage('people_search.html');     
    }
}

function acceptFriendRequest(pk, userName){
    var accept_info = {username:localStorage.getItem('username'), pk:pk};
    setUpAjax();
    $.ajax({
        url: 'http://localhost:8100/social/api/accept-friend-request/',
        type: "POST",
        data: accept_info,
        success: function(result){
            var resultParse = JSON.parse(result);
            console.log(resultParse);
            var successStatus = resultParse["status"];
            if(successStatus == true){
                $("#"+String(userName)).hide(500);
                console.log("accepted_friend");
            }
        },
        error: function(xhr){
            $("#error-message").text(xhr.responseText).show();
            console.log(xhr.responseText);
        }
    })
}

function denyFriendRequest(pk, userName){
    var deny_info = {username:localStorage.getItem('username'), pk:pk};
    setUpAjax();
    $.ajax({
        url: 'http://localhost:8100/social/api/deny-friend-request/',
        type: "POST",
        data: deny_info,
        success: function(result){
            var resultParse = JSON.parse(result);
            console.log(resultParse);
            var successStatus = resultParse["status"];
            if(successStatus == true){
                $("#"+String(userName)).hide(500);
                console.log("denied friend");
            }
        },
        error: function(xhr){
            $("#error-message").text(xhr.responseText).show();
            console.log(xhr.responseText);
        }
    })
}

function send_friends_request(id){
   var friend_request_info = {username:localStorage.getItem('username'), user_id:id};
   setUpAjax();
    $.ajax({
        url: 'http://localhost:8100/social/api/send-friend-request/',
        type: "POST",
        data: friend_request_info,
        success: function(result){
            var resultParse = JSON.parse(result);
            console.log(resultParse);
            var successStatus = resultParse["status"];
            if(successStatus == true){
                $("[name="+id+"]").text("Friend Request Sent!");
                console.log("Successful sent request");
            }
        },
        error: function(xhr){
            $("#error-message").text(xhr.responseText).show();
        }
    })
}

function getFriendShipRequest(){
    var friend_request_info = {username:localStorage.getItem('username')};
    setUpAjax(); 
       $.ajax({
        url: 'http://localhost:8100/social/api/friend-request/',
        type: "GET",
        data: friend_request_info,
        success: function(result){
        var resultParse = JSON.parse(result)
        console.log(resultParse);
        var successStatus = resultParse["status"];
        $("#friend_request_body_id").empty();
        if(successStatus === true){
            var request_friend_result = resultParse["result"];
            console.log("make me miss");
            for(var index=0; index < request_friend_result.length; index++){
                $("#friend_request_body_id").append('<div id='+request_friend_result[index].username+' class="row"></div>');
                var reqMessage = request_friend_result[index].message;
                $("#"+request_friend_result[index].username).append('<div class="col-md-3">'+reqMessage+'</div>');
                $("#"+request_friend_result[index].username).append('<div class="col-md-3"><button id="accept-request-button" \
                    name="'+request_friend_result[index].pk+'" onclick=acceptFriendRequest('+request_friend_result[index].pk+ "," +request_friend_result[index].username+') class="btn-link">Accept</button></div>');
                 $("#"+request_friend_result[index].username).append('<div class="col-md-3"><button id="accept-request-button" \
                    name="'+request_friend_result[index].pk+'" onclick=denyFriendRequest('+request_friend_result[index].pk+ "," +request_friend_result[index].username+') class="btn-link">Deny</button></div>');
            }
        }
     },
      error: function(xhr){
            $("#error-message").text(xhr.responseText).show();
            console.log(xhr);
      }
    });
}