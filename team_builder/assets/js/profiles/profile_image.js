(function() {
    /**
     * Initialization settings
     *
     * Creates various constants and images
     *
     * Various bits of this code was created with the help of the FabricJS
     * demos found here: http://fabricjs.com/demos/
     */

  // Create a getElementById shortcut
  const $ = function(id){return document.getElementById(id)};

  let drawingColor = $('drawing-color'),
      drawingLineWidth = $('drawing-line-width');


  // Get the hidden profile pic
  let imgElement = $('my-image');
  let imgInstance = new fabric.Image(imgElement, {});
  imgInstance.set({
      top: 0,
  });


  if (imgElement) {
    var imgHeight = imgElement.height;
    var imgWidth= imgElement.width;
  }


  // get the site wide profile pic
  let siteImgElement = $('site-image');
  let siteImgInstance = new fabric.Image(siteImgElement, {});
  siteImgInstance.set({
      top: 0,
  });

  let siteImgHeight = siteImgElement.height;
  let siteImgWidth = siteImgElement.width;


  // Initializes the canvas element
  // The canvas size is chosen based upon if the user has an avatar
  if (imgElement) {
    var canvas = this.__canvas = new fabric.Canvas('c', {
      isDrawingMode: true, width: imgWidth, height: imgHeight,
      // This prevents the avatar image from going to the front of the canvas
      // during rotation mode
      preserveObjectStacking: true
    });
  } else {
      var canvas = this.__canvas = new fabric.Canvas('c', {
      isDrawingMode: true, width: siteImgWidth, height: siteImgHeight,
      // This prevents the avatar image from going to the front of the canvas
      // during rotation mode
      preserveObjectStacking: true
    });
  }



  // Gets the main html form
  let form = $('theForm');

  // Canvas drawing image options
  canvas.freeDrawingBrush.color = drawingColor.value;

  fabric.Object.prototype.transparentCorners = false;

  // Adds either the site image, or the profile image to the canvas
  // depending on if the user has a profile image
  if (imgElement) {
    canvas.add(imgInstance)
  } else {
    canvas.add(siteImgInstance)
  }

  /** Various button/form settings and their respective functions */

  let clearCanvas = $('clear-canvas');
    /**
     * Deletes all of the drawings the user has created
     *
     * A new white background will be added to the canvas and redrawn
     */
  clearCanvas.onclick = function() {
      canvas.setHeight(siteImgHeight);
      canvas.setWidth(siteImgWidth);
      canvas.clear()
      canvas.backgroundColor='white';
      canvas.renderAll;
  };

  let clearCanvasWithPic = $('clear-canvas-with-pic');

  // Checks if the user has a profile picture. If not, don't create
  // the onclick method
  if (clearCanvasWithPic !== null) {
    clearCanvasWithPic.onclick = function() {
        /**
        * Deletes all of the drawings the user has created
        *
        * Redraws the user's profile picture
         * and scales the canvas accordingly
         */
      canvas.setHeight(imgHeight);
      canvas.setWidth(imgWidth);
      canvas.clear();

      // Get the hidden profile pic again to override imgInstance
      // If we use the old imgInstance it keeps position data
      let imgElement = $('my-image');
      let imgInstance = new fabric.Image(imgElement, {});
      imgInstance.set({
          top: 0,
      });

      canvas.add(imgInstance);
      canvas.renderAll;
    };
  }

  let clearCanvasSitePic = $('clear-canvas-with-site-pic');
  clearCanvasSitePic.onclick = function() {
    /**
     * Deletes all of the drawings the user has created
     *
     * A new canvas showing the site logo will be added to the canvas and
     * redrawn. Scaled accordingly
     */
      canvas.setHeight(siteImgHeight);
      canvas.setWidth(siteImgWidth);
      canvas.clear();

      // Get the hidden site image again to override imgInstance
      // If we use the old siteImgInstance it keeps position data
      let siteImgElement = $('site-image');
      let siteImgInstance = new fabric.Image(siteImgElement, {});
      siteImgInstance.set({
          top: 0,
      });

      canvas.add(siteImgInstance);
      canvas.renderAll;
  };

  // Creates the saveImageButton which lets a user submit the html form
  let saveImageButton = $('save-image');
  saveImageButton.onclick = saveImage;


  function saveImage () {
      /**
       * Takes the image drawn on the canvas and adds it to the html form
       *
       * Then submits the form.
       */
      let dataUrl= $('data-url')
      let imageInfo = canvas.toDataURL();
      dataUrl.value = imageInfo;
      form.submit()
  }


  // Creates the saveImageButton which lets a user submit the html form
  let drawingToggle= $('drawing-toggle');
  drawingToggle.onclick = toggleDrawing;

  function toggleDrawing() {
      /**
       * Toggles whether or not the canvas is in drawing mode.
       */
      let currentMode = canvas.isDrawingMode

      if (currentMode) {
          canvas.isDrawingMode = false
      } else {
          canvas.isDrawingMode = true
      }
  }

  // Creates the saveImageButton which lets a user submit the html form
  let rotate90 = $('rotate-90');
  rotate90.onclick = rotate;

  function rotate() {
      /**
       * This function redraws and rotates the canvas and all the images on it
       *
       * The rotate90 button gets unchecked as well
       */
      // uncheck the rotate90
      rotate90.checked = false;

      // Get the old canvas's height and width so the canvas can be swapped
      let oldHeight = canvas.height;
      let oldWidth = canvas.width;

      canvas.setHeight(oldWidth);
      canvas.setWidth(oldHeight);

      let height = canvas.height;
      let width = canvas.width;

      canvas.renderAll()

      console.log(canvas.height, canvas.width)

      let allObjects = canvas.getObjects();

      // loop through each object in the canvas and flip it
      for (let i = 0; i < allObjects.length; i++) {
        // The first item on the canvas is the main image.
        // It just needs to rotate. All other items rotate and move
        // in relationship to this image. Thus we need to separate them.
        if (i === 0) {

          // rotate the main canvas
          let object = allObjects[i];

          let rotation = object.angle;

          // Depending on the rotation the image will need to be
          // placed in a different corner of the screen.
          if (rotation === 0) {
            object.rotate(90);
            object.left = width;
            object.top = 0;

          } else if (rotation === 90) {
            object.rotate(180);
            object.left = width;
            object.top = height;

          } else if (rotation === 180) {
            object.rotate(270);
            object.left = 0;
            object.top = height;

          } else if (rotation === 270) {
            object.rotate(0);
            object.left = 0;
            object.top = 0;
          }


        }

      }
      canvas.renderAll();
    }


  // Adds the ability to add a circle to the canvas
  let addCircleButton = $('add-circle');
  addCircleButton.onclick = addCircle;

  function addCircle () {
    /**
     * Adds a circle to the canvas of a certain color
     *
     * Side Effects:
     * Turns off drawing mode via function
     */
    turnOffDrawingMode()
      let circle = new fabric.Circle({
        radius: 25,
        fill: drawingColor.value,
        originX: 'center',
        originY: 'center',
      });
      canvas.add(circle).centerObjectH(circle).centerObjectV(circle).renderAll();
  }

  // Adds the ability to add a square to the canvas
  let addSquareButton = $('add-square');
  addSquareButton.onclick = addSquare;

  function addSquare () {
    /**
     * Adds a square to the canvas of a certain color
     *
     * Side Effects:
     * Turns off drawing mode via function
     */
    turnOffDrawingMode()
    let rect = new fabric.Rect({
      fill: drawingColor.value,
      width: 40,
      height: 40,
      originX: 'center',
      originY: 'center',
    });
    canvas.add(rect).centerObjectH(rect).centerObjectV(rect).renderAll();

  }

  // Adds the ability to add a triangle to the canvas
  let addTriangleButton = $('add-triangle');
  addTriangleButton.onclick = addTriangle;

  function addTriangle() {
    /**
     * Adds a triangle to the canvas of a certain color
     *
     * Side Effects:
     * Turns off drawing mode via function
     */
    turnOffDrawingMode()
      let triangle = new fabric.Triangle({
        width: 43,
        height: 43,
        fill: drawingColor.value,
      });
      canvas.add(triangle).centerObjectH(triangle).centerObjectV(triangle).renderAll();
  }


  let removeSelectedButton = $('remove-selected');
  removeSelectedButton.onclick = removeSelected;

  function removeSelected () {
    /**
     * Removes the currently selected item if applicable
     *
     * Otherwise ignore
     */
    let selected = canvas.getActiveObject();

    // Check if the object exists
    if (selected) {
      canvas.remove(selected)
    }
  }

  function turnOffDrawingMode () {
    /**
     * Turns off the canvas drawing mode
     *
     * It also checks the rotate/move mode box
     */
    drawingToggle.checked = true;
    canvas.isDrawingMode = false
  }

  function turnOnDrawingMode () {
    /**
     * Turns on the canvas drawing mode
     *
     * It also un-checks the rotate/move mode box
     */
    drawingToggle.checked = false;
    canvas.isDrawingMode = true
  }

  drawingColor.onchange = function() {
    canvas.freeDrawingBrush.color = this.value;
  };

  drawingLineWidth.onchange = function() {
    turnOnDrawingMode();
    canvas.isDrawingMode = true;
    canvas.freeDrawingBrush.width = parseInt(this.value, 10) || 1;
    this.previousSibling.innerHTML = this.value;
  };

})();