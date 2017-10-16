function FillTable()
{
	window.SERVER = window.location.protocol + '//' + window.location.host; 

	if(location.protocol==='file:') window.SERVER = "http://localhost";

	
	var vehicle_list_url = window.SERVER + "/getAllvehicles";
	//var vehicle_list_url = "https://api.myjson.com/bins/3abx2";
	$.get( vehicle_list_url, 
			function( data,status ) 
			{
  				//alert( "Data Loaded: " + data );
  				//alert( "Status: " + status );

  				if (status==='success')
  				{
  					var tbody = $('table > tbody');

  					var vehicles = data; // vehicles list

  					sessionStorage.setItem('VLIST', JSON.stringify(vehicles));	// store vehicle list locally in browser for this session only

  					for (var i = 0; i < vehicles.length; i++) 
  					{
  						var vehicle = vehicles[i];

  						var tabledata = "";

  						var vehicle_properties = ['vid','vname','last_updated'];

  						for (var key in vehicle_properties)
  						{
  							tabledata += "<td>" + vehicle[vehicle_properties[key]] + "</td>" ;
  						}

  						tbody.append(
  										"<tr>" +
	  										tabledata +
	  										"<td>" + "<button type='button' class='btn btn-default btn-sm'>OFF</button>" + "</td>" +
  										"</tr>"
  									);
  					}
  					
  					
  					tbody.find("button").click(function(){this,handleTracking(tbody.find("button").index(this))})

  					//fill the session storage if not present already
  					if(sessionStorage.getItem("TRACKING_LIST")===null)
					{
						var currently_tracking = [];
						
						for (var i = 0; i < vehicles.length; i++) 
						{
							currently_tracking[i] = false;
						};
						
						sessionStorage.setItem("TRACKING_LIST",JSON.stringify(currently_tracking));	// set to blank array
					}

  					// decorate the buttons
  					var currently_tracking = JSON.parse(sessionStorage.getItem("TRACKING_LIST"));
  					var buttons = $('table > tbody').find("button");

  					for (var i = 0; i < currently_tracking.length; i++) 
  					{
  						var button = buttons.eq(i)	// select the ith button
  						if(currently_tracking[i]==false)
  						{
  							// do nothing as buttons are by default initialused to off
  						}
  						else
  						{
  							button.removeClass("btn-default")
  							button.addClass("btn-info")
  							button.html("ON")
  						}
  					}

  					//fadeout update button and set html to UPDATE from PLEASE WAIT...
					var u_btn = $("#update_btn")
					u_btn.fadeOut()
					u_btn.html("UPDATE")

  					return;
  				}
  				else
  				{
  					var c = confirm("Couldn't fetch Vehicles from server. Try again?");
  					if(c) FillTable();
  					else return;
  				}
			}
		  );

		
		//click update button to reload page (HTML session storage will not be deleted)
		$("#update_btn").click(function()
										{
											sessionStorage.setItem("ISAmapVdataUrl",window.ISAmapVdataUrl);	//update vehicleData url
											location.reload();
										}
							  )
		
		console.log("VLIST : \n" + sessionStorage.getItem("VLIST"))
		if(sessionStorage.getItem("TRACKING_LIST")!==null)
		console.log("TRACKING_LIST : " + sessionStorage.getItem("TRACKING_LIST"))

}


function handleTracking(index)
{
	var vlist = JSON.parse(sessionStorage.getItem("VLIST"));

	var vehicle = vlist[index];
	var vid = vehicle.vid;
	var vname = vehicle.vname;
	//alert(vname);return;

	
	var currently_tracking =  JSON.parse(sessionStorage.getItem("TRACKING_LIST"));	// get the current list
	
	if(currently_tracking[index]==false) // not tracking already
	{
		currently_tracking[index] = true ;	// add the vid to currently_tracking
	}
	else	// if already present, then remove
	{
		currently_tracking[index] = false ; // remove from tracking
	}

	//update buttons
	var buttons = $('table > tbody').find("button");
	for (var i = 0; i < buttons.length; i++) 
	{
		var button = buttons.eq(i);

		if(currently_tracking[i]==false)
		{
			button.removeClass("btn-info")
			button.addClass("btn-default")
			button.html("OFF")
		}
		else
		{
			button.removeClass("btn-default")
			button.addClass("btn-info")
			button.html("ON")
		}
	}

	// update session storage
	sessionStorage.setItem("TRACKING_LIST",JSON.stringify(currently_tracking));

	//create ISAmapVdataUrl
	var v2trackJSON = [];

	for (var i = 0; i < vlist.length; i++) 
	{
		var vehicle = vlist[i];
		var vid = vehicle.vid;
		
		if(currently_tracking[i]===true)
			v2trackJSON.push(vid);

	}

	window.ISAmapVdataUrl = window.SERVER + '/getpos?jsonstring={"vids":' + JSON.stringify(v2trackJSON) + ',"waypoints":5}';
	
	console.log(window.ISAmapVdataUrl);

	// show update button
	$("#update_btn").fadeIn()

	//location.reload();	// reload the page
}


FillTable();



