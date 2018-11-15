<template>
  <div >
    <!-- Header -->
    <h1>Database {{ database_name }} contains {{ num_images }} images</h1>
    <div>
      <router-link to="/about">About</router-link>
    </div>

    <!-- QueryDropZone -->
    <div class = "dropzone-div">
      <vue-dropzone 
        ref = "dropzone" 
        id = "dropzone" 
        :options = "dropConfig"
        :useCustomSlot = true
        @vdropzone-complete = "on_query_complete"
        >
          <div class="dropzone-custom-content">
            <h3 class="dropzone-custom-title">Drop photo to search</h3>
            <div class="subtitle">...or click to select a file</div>
          </div>              
        </vue-dropzone>
    </div>

    <!-- Yes I'm using a table. So 1996 -->
    <div>
    <template v-for="(search_image, search_idx) in search_images">
      <table>
          <tr>
            <!-- QueryImage -->
            <td class = "search-image">
              <img :src="search_image" width=100 height=100>
              <!-- <h3></h3> -->
            </td>

            <td class = "equals-image">
              <img src="/static/equals.png" width=100 height=100>
            </td>

            <!-- QueryResultsView -->
            <template v-for="(item, _) in search_results[search_idx]">
              <td class = "result-image">
                <img :src="item.filename" width=100 height=100>
                <!-- <h3>{{item.class}}</h3> -->
              </td>
            </template>
          </tr>
        </table>
      </template>
    </div>
  </div>
</template>

<script>
import vueDropzone from "vue2-dropzone";

export default {
  data () {
    return {
      num_images: 0,
      database_name: "offline",
      search_images: [],
      search_results: [],

      dropConfig: {
        url: "http://hiro_wifi:1980/v1/search",
        maxFiles: 5,
        maxFilesize: 2,
        acceptedFiles: "image/*,.png,.jpg,.gif,.bmp,.jpeg",
        addRemoveLinks: true,
        resizeWidth: 256,
        //resizeHeight: 256,
        createImageThumbnals: false,
        //thumbnailWidth: 128,
        //thumbnailHeight: 128,
        dictRemoveFile: "Search again",
        parallelUploads: 1,
      }
    }
  },

  components: {
    vueDropzone
  },

  methods: {
    get_database_info() 
    {
      const http = new XMLHttpRequest();
      const url = "http://hiro_wifi:1980/v1/images"
      http.open("GET", url);
      http.send();
      http.onreadystatechange = (e) => 
      {
        if (http.readyState == 4 && http.status == 200)
        {
          var response = JSON.parse(http.responseText);
          this.num_images = response.num_images
          this.database_name = response.database_name
        }
      }
    },

    blob_to_data_url(blob, callback) 
    {
      // FileReaders are asynchronous, so the callback is mandatory
      var a = new FileReader();
      a.onload = function(e) { callback(e.target.result); }
      a.readAsDataURL(blob);
    },

    // Dropzone.js converts file to base64 and prefixes it with the MIME type.
    // This might be the right thing to do, but it's not how curl works and it
    // breaks sever-side PIL.Image.open().
    // So, let's strip the metadata and convert back to raw bytes to keep the server happy.
    // https://stackoverflow.com/questions/4998908/convert-data-uri-to-file-then-append-to-formdata
    data_url_to_blob(dataURL) 
    {
        // convert base64/URLEncoded data component to raw binary data held in a string
        var byteString;
        if (dataURL.split(',')[0].indexOf('base64') >= 0)
            byteString = atob(dataURL.split(',')[1]);
        else
            byteString = unescape(dataURL.split(',')[1]);

        // separate out the mime component
        var mimeString = dataURL.split(',')[0].split(':')[1].split(';')[0];

        // write the bytes of the string to a typed array
        var ia = new Uint8Array(byteString.length);
        for (var i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }

        return new Blob([ia], {type:mimeString});
    },

    // Append the search image and results as a new table row, and reset the dropzone
    // for another search
    on_query_complete(file)
    {
      if (!file || !file.xhr || !file.xhr.response)
      { 
        console.log("query failed: " + file)
        return
      } 

      console.log("query complete: " + file + " : " + file.xhr.response)

      // reset the dropzone so user can search again
      this.$refs.dropzone.removeAllFiles(true)

      var new_results = []

      var dict = JSON.parse(file.xhr.response)
      for (var key in dict)
      {
        if (dict.hasOwnProperty(key))
        {
          var search_result = dict[key]

          // NOTE: in Vue.js we don't modify the DOM directly
          // Everything is data-driven, so we update component.variable and the component will auto-refresh
          new_results.push( { class: search_result.class, filename: search_result.filename } )
        }
      }

      // Copy the search image to the left-hand side of the table row.
      // We do this because, for every search, we append a new row to the page and reset the Dropzone.
      // Unfortunately Dropzone only gives us a File/Blob, so we need to load it into a dataURL to show it,
      // which is an asynchronous operation:
      var _search_images = this.search_images
      var _search_idx = this.search_images.length
      this.blob_to_data_url( file, 
        function(dataURL)
        {
          // Vue.js Common Gotchas:
          // When you modify an Array by directly setting an index (e.g. arr[0] = val) 
          // or modifying its length property [Vue.js doesn't know and the DOM won't update]. 
          // Always modify arrays by using an Array instance method, or replacing it entirely. 
          _search_images.splice( _search_idx, 1, dataURL )
        } 
      )

      this.search_images.push(file.name) // push filename as a placeholder; dataURL will be available asynchronously
      this.search_results.push(new_results)
    }
  },

  created()
  {
    this.get_database_info()
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.dropzone-div {
  padding: 25px;
}

.dropzone {
  margin: 0 auto;
  width: 250px;
  height: 150px;
  min-height: 0px;
  padding: 5px;
}   

.search-image {
  width: 10%;
  height: auto;
  /* border: dashed 3px red; */
  background-color: rgb(255, 255, 255);
}

.equals-image {
  width: 10%;
  height: auto;
}

.result-image {
  width: 10%;
  height: auto;
}

h1, h2, h3 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #1951ec;
}

table {
  margin: 0 auto;
  table-layout: fixed;
  width: 50%;
  border-collapse: collapse;
  /* border: 5px solid rgb(0, 255, 0); */
}

tr {
  padding: 2px;
  /* border: 1px solid rgb(255, 0, 0); */
}

td {
  /* border: 1px solid rgb(25, 0, 255); */
}

</style>
