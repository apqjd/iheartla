function drawArrow( startElement, endElement, style='' , color='blue', 
  offsetVerticalX=0, offsetStartY=0, offsetEndY=0, offsetEndX=20) {
    // This pseudocode creates an SVG element for each "arrow". As an alternative,
    // we could always have one SVG element present in the document
    // with absolute position 0,0 (or along the right side of the window)
    // whose width and height allows us to draw anywhere.
    // Then we would add and remove child nodes as needed.
    // You can use vanilla JS or svg.js or snap.js. Probably svg.js is a good fit.
    // Create a new SVG node
    // var svg = SVG().addTo('body').size('100%', '100%').move(-1010, -410);
    // console.log(`start is ${startElement}, end is ${endElement}`)
    // console.log(`svg is ${svg}`);
    var body = document.querySelector("body");
    var style = window.getComputedStyle(body);
    var newWidth = parseInt(style.width, 10) + parseInt(style.marginLeft, 10) + parseInt(style.marginRight, 10);
    var newHeight = parseInt(style.height, 10);
    var svg = SVG().addTo('body').size(`${newWidth}px`, `${newHeight}px`).attr('left', '0px');
    // Name it for selector queries so you can style it and also delete it
    svg.addClass("arrow")
    // Get the position of the start and end elements in absolute coordinates
    // console.log(startElement);
    // console.log(endElement);
    var bodyRect = body.getBoundingClientRect();
    var startRect = startElement.getBoundingClientRect();
    var startCenterX = startRect.x + startRect.width/2;
    var startCenterY = startRect.y + startRect.height/2;
    var endRect = endElement.getBoundingClientRect();
    var endCenterX = endRect.x + endRect.width/2;
    var endCenterY = endRect.y + endRect.height/2;
    var marginLeft = parseInt(style.marginLeft, 10)
    var bodyWidth = parseInt(style.width, 10)
    var marginTop = parseInt(style.marginTop, 10)
    // console.log(style); 
    var arrowSize = 5;
    // var offsetEndX = 20;
    // var endPointX = endCenterX - bodyRect.x + marginLeft;
    // var endPointY = endCenterY - bodyRect.y + marginTop;
    var endPointX = bodyWidth+marginLeft-offsetEndX;
    var endPointY = endCenterY - bodyRect.y + marginTop;
    // console.log(`marginTop is ${marginTop}`);
    // svg.path(`M${startCenterX - bodyRect.x + marginLeft} ${startCenterY - bodyRect.y + marginTop} 
    svg.path(`M${bodyWidth+marginLeft-offsetEndX} ${startCenterY - bodyRect.y + marginTop+offsetStartY} 
      L ${bodyWidth+marginLeft+offsetVerticalX} ${startCenterY - bodyRect.y + marginTop+offsetStartY} 
      L ${bodyWidth+marginLeft+offsetVerticalX} ${endCenterY - bodyRect.y + marginTop+offsetEndY} 
      L ${endPointX} ${endPointY+offsetEndY} 
      L ${endPointX+arrowSize} ${endPointY-arrowSize+offsetEndY} 
      L ${endPointX} ${endPointY+offsetEndY} 
      L ${endPointX+arrowSize} ${endPointY+arrowSize+offsetEndY} 
      `).attr({fill: 'white', 'fill-opacity': 0, stroke: color, 'stroke-width': 1})
    svg.attr('offset', parseInt(style.marginLeft, 10))
    document.querySelector(".arrow").style.marginLeft = "0px"
}

function getSymTypeInfo(type_info){
  if(type_info.type == 'matrix'){
    content = "matrix, rows: " + type_info.rows + ", cols: " + type_info.cols;
  }
  else if(type_info.type == 'vector'){
    content = "vector, rows: " + type_info.rows;
  }
  else if(type_info.type == 'scalar'){
    content = "scalar";
  }
  else{
    content = "invalid type";
  }
  // console.log("type_info.type: " + type_info.type);

  return content;
};
function getGlossarySymInfo(symbol){
  content = ''
  data_list = sym_data[symbol];
  console.log(`symbol is ${symbol}, length is ${data_list.length}`)
  for (var i = 0; i < data_list.length; i++) {
      var data = data_list[i];
      content += `<div> In module ${data.def_module}<br>
      <a href="#${data.def_module}-${symbol}">${symbol}</a> is ${getSymTypeInfo(data.type_info)}`
      content += `` ;
      if (data.used_equations.length > 0) {
        content += `<br>${symbol} is used in ` ;
        for (var j = 0; j < data.used_equations.length; j++) {
          content += data.used_equations[j];
        }
      }
      content += `</div>`;
  }
  return `<span>${content}</span>`;
}
function parseSym(tag, symbol){
  data = sym_data[symbol];
  console.log(`You clicked ${symbol}`);
  if (typeof tag._tippy === 'undefined'){
    tippy(tag, {
        content: getGlossarySymInfo(symbol),
        placement: 'right',
        animation: 'fade',
        trigger: 'click', 
        // theme: 'material',
        showOnCreate: true,
        allowHTML: true,
        interactive: true,
        onShow(instance) {
          return true;  
        },
        onHide(instance) { 
          return true;  
        },
      });
  }
}
function parseAllSyms(){
  keys = [];
  for (var k in sym_data) { 
    keys.push(k);
  }
  keys.sort();
  info = '<p>Glossary of symbols</p>'
  for (i = 0; i < keys.length; i++) {
    k = keys[i];
    diff_list = sym_data[k];
    diff_length = diff_list.length;
    if (diff_length > 1) {
      content = `<span onclick="parseSym(this, '${k}');"><span class="clickable_sym">${k}</span>: ${diff_length} different types</span><br>`;
    }
    else{
      if (diff_list[0].is_defined){
        content = `<span onclick="parseSym(this, '${k}');"><span class="clickable_sym">${k}</span>: defined </span><br>`;
      }
      else{
        content = `<span onclick="parseSym(this, '${k}');"><span class="clickable_sym">${k}</span>: ${diff_list[0].desc}</span><br>`;
      }
    }
    // console.log(content);
    info += content;
  }
  // console.log(document.querySelector("#glossary"));
  tippy(document.querySelector("#glossary"), {
        content: info,
        placement: 'bottom',
        animation: 'fade',
        trigger: 'click', 
        allowHTML: true,
        interactive: true,
      }); 
}
function getSymInfo(symbol, func_name){
  content = '';
  var found = false;
  for(var eq in iheartla_data.equations){
    if(iheartla_data.equations[eq].name == func_name){
      for(var param in iheartla_data.equations[eq].parameters){
        if (iheartla_data.equations[eq].parameters[param].sym == symbol){
          type_info = iheartla_data.equations[eq].parameters[param].type_info;
          found = true;

          if(iheartla_data.equations[eq].parameters[param].desc){
            content = symbol + " is " + iheartla_data.equations[eq].parameters[param].desc + ", the type is " + getSymTypeInfo(type_info);
          }
          else{
            content = symbol + " is a parameter as a " + getSymTypeInfo(type_info);
          }
          break;
        }
      }
      if(found){
        break;
      }
      for(var param in iheartla_data.equations[eq].definition){
        if (iheartla_data.equations[eq].definition[param].sym == symbol){
          type_info = iheartla_data.equations[eq].definition[param].type_info;
          found = true;
          content = symbol + " is defined as a " + getSymTypeInfo(type_info);
          break;
        }
      }
      if(found){
        break;
      }
    }
  }
  return content;
}
function showSymArrow(tag, symbol, func_name, type='def', color='blue', 
  offsetVerticalX=0, offsetStartY=0, offsetEndY=0, offsetEndX=20){
  tag.setAttribute('class', `highlight_${color}`);
  if (type === 'def' ) {
    // Point to usage
    const matches = document.querySelectorAll("[case='equation'][sym='" + symbol + "'][func='"+ func_name + "'][type='use']");
    for (var i = matches.length - 1; i >= 0; i--) {
      matches[i].setAttribute('class', `highlight_${color}`);
      // console.log(`${i} is ${matches[i].innerHTML}`)
      if (matches[i] !== tag && matches[i].tagName.startsWith("MJX")) {
        drawArrow(tag, matches[i],'',color,offsetVerticalX, offsetStartY, offsetEndY, offsetEndX);
      }
    }
    // prose label
    // const prose = document.querySelectorAll("mjx-mi[sym='" + symbol + "'][module='"+ func_name + "']");
    // if (prose !== 'undefined') {
    //   for (var i = prose.length - 1; i >= 0; i--) {
    //     // matches[i].setAttribute('class', `highlight_${color}`);
    //     if (prose[i] !== tag ) {
    //       drawArrow(tag, prose[i], '',color,offsetVerticalX, offsetStartY, offsetEndY, offsetEndX);
    //     }
    //   }
    // }
  }
  else{
    // Point from def
    const matches = document.querySelectorAll("[case='equation'][sym='" + symbol + "'][func='"+ func_name + "'][type='def']");
    // console.log(`matches.length is ${matches.length}`)
    if (matches !== 'undefined' && matches.length !== 0) {
      // console.log(`${matches.length} prose`)
      for (var i = matches.length - 1; i >= 0; i--) {
        // console.log(`${i} is ${matches[i].innerHTML}, tag is ${matches[i].tagName}`)
        matches[i].setAttribute('class', `highlight_${color}`);
        if (matches[i] !== tag && matches[i].tagName.startsWith("MJX")) {
          drawArrow(matches[i], tag, '',color,offsetVerticalX, offsetStartY, offsetEndY, offsetEndX);
        }
      }
    }
    else{
      // defined in prose
      const prose = document.querySelectorAll("mjx-mi[sym='" + symbol + "'][module='"+ func_name + "'][type='def']");
      if (prose !== 'undefined') {
        for (var i = prose.length - 1; i >= 0; i--) {
          // matches[i].setAttribute('class', `highlight_${color}`);
          if (prose[i] !== tag ) {
            drawArrow(prose[i], tag, '',color,offsetVerticalX, offsetStartY, offsetEndY, offsetEndX);
          }
        }
      }
    }
  }
}
function highlightSym(symbol, func_name, color='red'){
  const matches = document.querySelectorAll("mjx-texatom[sym='" + symbol + "'][func='" + func_name + "']");
  for (var i = matches.length - 1; i >= 0; i--) {
    matches[i].setAttribute('class', `highlight_${color}`);
  }
}
function highlightProse(symbol, func_name, color='red'){
  const matches = document.querySelectorAll("[sym='" + symbol + "'][module='" + func_name + "']");
  for (var i = matches.length - 1; i >= 0; i--) {
    matches[i].setAttribute('class', `highlight_${color}`);
  }
}
function onClickProse(tag, symbol, func_name, type='def') {
  console.log(`onClickProse, ${tag}, ${symbol}, ${func_name}`);
  highlightSym(symbol, func_name);
  highlightProse(symbol, func_name);
  if (typeof tag._tippy === 'undefined'){
    tippy(tag, {
        content: getSymInfo(symbol, func_name),
        placement: 'bottom',
        animation: 'fade',
        trigger: 'click', 
        theme: 'light',
        showOnCreate: true,
        onShow(instance) {
          // closeOtherTips();
          return true;  
        },
        onHide(instance) {
          resetState();
          return true;  
        },
      });
  }
}
/**
 * Click a symbol in equations
 *
 * @param {object} tag The current xml tag
 * @param {string} symbol The symbol name
 * @param {string} func_name The equation/context name
 * @param {string} type The type for the symbol: 'def','prose','use'
 * @return 
 */
function onClickSymbol(tag, symbol, func_name, type='def') {
  // console.log(`the type is ${type}, sym is ${symbol}`)
  resetState();
  closeOtherTips();
  highlightProse(symbol, func_name);
  showSymArrow(tag, symbol, func_name, type, color='red');
    // d3.selectAll("mjx-mi[sym='" + symbol + "']").style("class", "highlight");
  if (typeof tag._tippy === 'undefined'){
    tippy(tag, {
        content: getSymInfo(symbol, func_name),
        placement: 'bottom',
        animation: 'fade',
        trigger: 'click', 
        theme: 'light',
        showOnCreate: true,
        onShow(instance) {
          // closeOtherTips();
          return true;  
        },
        onHide(instance) {
          resetState();
          return true;  
        },
      });
  }
  // console.log("clicked: " + symbol + " in " + func_name); 
};
function onClickEq(tag, func_name, sym_list) { 
  closeOtherTips();
  resetState();
  var colors =['red', 'YellowGreen', 'DeepSkyBlue', 'Gold', 'HotPink', 'Tomato', 'Orange', 'DarkRed', 'LightCoral', 'Khaki']
  content = "This equation has " + sym_list.length + " symbols\n";
  var offsetVerticalX = 0;
  var offsetStartY = 0;
  var offsetEndY = 0;
  var offsetEndX = 30;
  for (var i = sym_list.length - 1; i >= 0; i--) {
    sym = sym_list[i];
    content += getSymInfo(sym_list[i], func_name) + '\n';
    var symTag = tag.querySelector("[case='equation'][sym='" + sym_list[i] + "']");
    const matches = document.querySelectorAll("[case='equation'][sym='" + sym_list[i] + "']");
    // console.log(`tag is ${tag}, symTag is ${symTag}, matches is ${matches}, sym is ${sym_list[sym]}`);
    offsetVerticalX += 5;
    offsetStartY += 2;
    offsetEndY += 2;
    offsetEndX -= 5;
    if (symTag !== null){
      console.log(`symTag is ${symTag}`);
      if (i === sym_list.length - 1) {
        showSymArrow(symTag, sym_list[i], func_name, 'def', colors[i], offsetVerticalX, offsetStartY, offsetEndY, offsetEndX);
      }
      else{
        showSymArrow(symTag, sym_list[i], func_name, 'use', colors[i], offsetVerticalX, offsetStartY, offsetEndY, offsetEndX);
      }
    }
  }
  if (typeof tag._tippy === 'undefined'){
    tippy(tag, {
        content: content,
        placement: 'bottom',
        animation: 'fade',
        trigger: 'click', 
        showOnCreate: true,
        onShow(instance) { 
          tag.setAttribute('class', 'highlight_fake');
          // console.log('onShow');
          return true;  
        },
        onHide(instance) {
          resetState();
          return true;  
        },
      });
  }
};
function resetState(){
  removeArrows();
  removeSymHighlight();
}
function removeArrows(){
  var matches = document.querySelectorAll(".arrow");
  if (matches) {
    for (var i = matches.length - 1; i >= 0; i--) {
      document.querySelector("body").removeChild(matches[i]);
    }
  }
}
function removeSymHighlight(){
  const matches = document.querySelectorAll("[class^=highlight]");
  for (var i = matches.length - 1; i >= 0; i--) {
    matches[i].removeAttribute('class');
  }
}
function closeOtherTips(){
  const matches = document.querySelectorAll("[class^=highlight]");
  for (var i = matches.length - 1; i >= 0; i--) {
    if (typeof matches[i]._tippy !== 'undefined'){
      matches[i]._tippy.hide();
    }
  }
};
function onClickGlossary(){
  alert('You clicked the glossary');
};