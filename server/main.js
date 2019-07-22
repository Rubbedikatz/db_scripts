var width = 960,
    height = 500,
    focused = null,
    geoPath,

// insert div to contain svg and controls
frame = d3.select("body")
  .append("div")
  .attr("width", width)
  .attr("height", height+10)
  .attr("style", "text-align:center"),
  
// insert svg element as canvas
svg = frame.append("svg")
    .attr("width", width)
    .attr("height", height),

// mark g objects as "states" so they're rendered correctly by d3
g = svg.append("g")
  .append("g")
    .attr("id", "states"),

// define div for the tooltip
tooltip = d3.select("body").append("div")	
    .attr("class", "tooltip")				
    .style("opacity", 0);

d3.queue()
	.defer(d3.json, "./data/bundeslander.json")
	.defer(d3.json, "./data/cities_new.json")
  .awaitAll(render_map);
  

// insert states data
function render_map(error, result_data) {

  frame.append("input")
      .attr("type", "range")
      .attr("min", 0)
      .attr("max", result_data[1].length-1)
      .attr("step", "1")
      .attr("id", "slider")
      .attr("value", 0)
      .on("input", function input() {
        sliderUpdate(this, result_data[1]);
      });

    // get max and min delay of all trips to calculate color scale domain
  var delays = [];
  result_data[1].forEach(function (month, index) {
    for (var station in month.features) {
      delays.push(month.features[station]["properties"]["mean_delay"]);
    }
  });
  var delay_max = Math.max(...delays),
      delay_min = Math.min(...delays),
      delay_mid = (delay_max+delay_min)/2,
      myColor = d3.scaleLinear()
                        .domain([delay_min, delay_mid, delay_max])
                        .range(["green", "yellow", "red"]);
  
  var bundeslander = result_data[0],
      stations = result_data[1]

  var bounds = d3.geoBounds(bundeslander),
    bottomLeft = bounds[0],
    topRight = bounds[1],
    rotLong = -(topRight[0]+bottomLeft[0])/2;
    center = [(topRight[0]+bottomLeft[0])/2+rotLong, (topRight[1]+bottomLeft[1])/2],
    
    // first projection to get outer bounds and scaleFator
    first_projection = d3.geoAlbers()
      .parallels([bottomLeft[1],topRight[1]])
      .rotate([rotLong,0,0])
      .translate([width/2,height/2])
      .center(center),

    bottomLeftPx = first_projection(bottomLeft),
    topRightPx = first_projection(topRight),
    scaleFactor = 1.00*Math.min(width/(topRightPx[0]-bottomLeftPx[0]), height/(-topRightPx[1]+bottomLeftPx[1])),
    
    // second projection for plotting states and stations
    second_projection = d3.geoAlbers()
      .parallels([bottomLeft[1],topRight[1]])
      .rotate([rotLong,0,0])
      .translate([width/2,height/2])
      .scale(scaleFactor*0.975*1000)
      .center(center);

  // create path object from projection to translate GeoJSON 
  geoPath = d3.geoPath().projection(second_projection);

  // insert and render states
  g.selectAll("path.feature")
      .data(bundeslander.features)
      .enter()
      .append("path")
        .attr("class", "feature")
        .attr("d", geoPath)
  
  // initialize stations with first dataset
  render_stations(stations, 0);

  function render_stations(station_data, index){
    // insert and render stations
    var circles = g.selectAll("circle.feature")
        .data(station_data[index].features);

      circles.enter().append("circle")
          .attr("class", "feature")
          .attr("cx", function(d){ return second_projection(d.geometry.coordinates)[0]; } )
          .attr("cy", function(d){ return second_projection(d.geometry.coordinates)[1]; } )
          .attr("r", function(d){ return d.properties.trips/500; })
          .attr("fill", function(d){return myColor(d.properties.mean_delay) })
          // add tooltips on mouseover
          .on("mouseover", function(d) {		
            tooltip.transition()		
                .duration(200)		
                .style("opacity", .9);		
            tooltip.html("<b>" + d.properties.name + "</b><br/>"  + "Avg. delay: " + Math.round(d.properties.mean_delay*100)/100 + " minutes" + "<br/>" + "Total trips: " + d.properties.trips)	
                .style("left", (d3.event.pageX) + "px")		
                .style("top", (d3.event.pageY - 28) + "px");	
            })					
          .on("mouseout", function(d) {		
            tooltip.transition()		
                .duration(500)		
                .style("opacity", 0);
            })
          // event for clicking on a station
          .on("click", clickStation)
          .merge(circles)
            .transition().duration(300)
            .attr("r", function(d){ return d.properties.trips/500; })
            .attr("fill", function(d){return myColor(d.properties.mean_delay) })
            // updating data loses focus, so we remove the black border...
            .style("stroke", "white");
          
          circles.exit().remove();
  };       


    function sliderUpdate(slider, data){
      // update size and color of circles based on the slider position
      render_stations(data, slider.value);

      g.transition()
        // ...and zoom back out to default
        .duration(300)
        .attr("transform", "translate("+ (width/2) +","+ (height/2) +")scale(1)translate("+ (-width/2) +","+ (-height/2) +")")
        .style("stroke-width", 1.75 +"px");
    };

    // this is run when a station is clicked
    function clickStation(d) {
      // set default non-zoom values
      var x = width/2,
          y = height/2,
          k = 1;

      // if the clicked station hasn't been in focus before click
      if ((focused === null) || !(focused === d)) {
        // set point to zoom in on
        var centroid = geoPath.centroid(d),
            x = +centroid[0],
            y = +centroid[1],
            k = 3; // zoom factor
        focused = d;
        // reset all circles to white borders, then paint focused one black
        g.selectAll("circle").style("stroke", "white");
        d3.select(this).style("stroke", "black");
      } 
      // if the clicked station was already in focus before click
      else {
        // leave zoom values as default -> zoom out
        focused = null;
        d3.select(this).style("stroke", "white");
      };

      // change pixel size of states
      // when k = 1 all sizes reset back to default
      g.transition()
        .duration(700)
        .attr("transform", "translate("+ (width/2) +","+ (height/2) +")scale("+ k +")translate("+ (-x) +","+ (-y) +")")
        .style("stroke-width", 1.75/k +"px")
        // shrink circle size even more to make them more distinguishable
        // when k=1 needs to match the initial number for radius set above
        .selectAll("circle")
          .attr("r", function(d){ return d.properties.trips/(300*k+200); });
      };
  };
      
