var width = 960,
    height = 500,
    focused = null,
    geoPath;

var svg = d3.select("body")
  .append("svg")
    .attr("width", width)
    .attr("height", height);

svg.append("rect")
    .attr("class", "background")
    .attr("width", width)
    .attr("height", height);

var g = svg.append("g")
  .append("g")
    .attr("id", "states");


// Define the div for the tooltip
var div = d3.select("body").append("div")	
    .attr("class", "tooltip")				
    .style("opacity", 0);

d3.json("./bundeslander.json", function(bundeslander) {


  var bounds = d3.geo.bounds(bundeslander),
      bottomLeft = bounds[0],
      topRight = bounds[1],
      rotLong = -(topRight[0]+bottomLeft[0])/2;
      center = [(topRight[0]+bottomLeft[0])/2+rotLong, (topRight[1]+bottomLeft[1])/2],
      
      projection_one = d3.geo.albers()
        .parallels([bottomLeft[1],topRight[1]])
        .rotate([rotLong,0,0])
        .translate([width/2,height/2])
        .center(center),

      bottomLeftPx = projection_one(bottomLeft),
      topRightPx = projection_one(topRight),
      scaleFactor = 1.00*Math.min(width/(topRightPx[0]-bottomLeftPx[0]), height/(-topRightPx[1]+bottomLeftPx[1])),
      
      final_projection = d3.geo.albers()
        .parallels([bottomLeft[1],topRight[1]])
        .rotate([rotLong,0,0])
        .translate([width/2,height/2])
        .scale(scaleFactor*0.975*1000)
        .center(center);

  geoPath = d3.geo.path().projection(final_projection);

  g.selectAll("path.feature")
      .data(bundeslander.features)
      .enter()
    .append("path")
      .attr("class", "feature")
      .attr("d", geoPath)

  // ##############################################
  
  function clickPath(d) {
    var x = width/2,
        y = height/2,
        k = 1;

    g.selectAll("text")
      .remove();
    if ((focused === null) || !(focused === d)) {
      var centroid = geoPath.centroid(d),
          x = +centroid[0],
          y = +centroid[1],
          k = 1.75;
      focused = d;
      d3.selectAll("circle").style("stroke", "white");
      d3.select(this).style("stroke", "black");
    } else {
      focused = null;
      d3.select(this).style("stroke", "white");
    };
  
    g.selectAll("path")
        .classed("active", focused && function(d) { return d === focused; });
   
    g.transition()
        .duration(500)
        .attr("transform", "translate("+ (width/2) +","+ (height/2) +")scale("+ k +")translate("+ (-x) +","+ (-y) +")")
        .style("stroke-width", 1.75/k +"px");
  }
  
 
  // ##############################################
      
    d3.json("./cities.json", function(cities) {
        
    var delays = [];
    for (var station in cities.features) {
      delays.push(cities.features[station]["properties"]["mean_delay"]);
    };
    var delay_max = Math.max(...delays),
        delay_min = Math.min(...delays),
        delay_mid = (delay_max+delay_min)/2
    var myColor = d3.scale.linear().domain([delay_min, delay_mid, delay_max])
        .range(["green", "yellow", "red"]);
    
       
    g.selectAll("circle.feature")
        .data(cities.features)
        .enter()
        .append("circle")
          .attr("class", "feature")
          .attr("cx", function(d){ return final_projection(d.geometry.coordinates)[0]; } )
          .attr("cy", function(d){ return final_projection(d.geometry.coordinates)[1]; } )
          .attr("r", function(d){ return d.properties.trips/500; })
          .attr("fill", function(d){return myColor(d.properties.mean_delay) })
          .on("mouseover", function(d) {		
            div.transition()		
                .duration(200)		
                .style("opacity", .9);		
            div	.html("<b>" + d.properties.name + "</b><br/>"  + "Durch. Versp.: " + Math.round(d.properties.mean_delay*100)/100 + " Minuten" + "<br/>" + "Fahrten: " + d.properties.trips)	
                .style("left", (d3.event.pageX) + "px")		
                .style("top", (d3.event.pageY - 28) + "px");	
            })					
          .on("mouseout", function(d) {		
            div.transition()		
                .duration(500)		
                .style("opacity", 0);	location
          })
          .on("click", clickPath);
        });
      
});


