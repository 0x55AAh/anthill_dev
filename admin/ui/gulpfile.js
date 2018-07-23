/* ------------------------------------------------------------------------------
 *
 *  # Gulp file
 *
 *  Basic Gulp tasks for Limitless template
 *
 *  Version: 1.1
 *  Latest update: Aug 20, 2016
 *
 * ---------------------------------------------------------------------------- */


// Include gulp
var gulp = require('gulp');


// Include our plugins
var jshint = require('gulp-jshint');
var less = require('gulp-less');
var minifyCss = require('gulp-clean-css');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var rename = require('gulp-rename');

var browserify = require('browserify');
var source = require('vinyl-source-stream');
var buffer = require('vinyl-buffer');
var transform = require('vinyl-transform');
var through2 = require('through2');


var ui_theme_dir = 'themes/limitless/';


// Lint task
gulp.task('lint', function() {
    return gulp
        .src(ui_theme_dir + 'static/js/core/app.js')                 // lint core JS file. Or specify another path
        .pipe(jshint())
        .pipe(jshint.reporter('default'));
});


// Browserify task
gulp.task('browserify', function() {
    var browserified = through2.obj(function (file, enc, next){
            browserify(file.path)
                .bundle(function(err, res){
                    file.contents = res;
                    next(null, file);
                });
        });
  return gulp.src([
      ui_theme_dir + 'static/js/plugins/extensions/reconnecting-websocket.js',
      ui_theme_dir + 'static/js/plugins/extensions/kurento-jsonrpc.js'
  ])
  .pipe(browserified)
  .pipe(rename({
        suffix: ".min"
  }))
  .pipe(uglify())
  .pipe(gulp.dest(ui_theme_dir + 'static/js/plugins/extensions'));
});


// Compile less files of a full version
gulp.task('less_full', function() {
    return gulp
        .src(ui_theme_dir + 'static/less/_main_full/*.less')         // locate /less/ folder root to grab 4 main files
        .pipe(less())                                 // compile
        .pipe(gulp.dest(ui_theme_dir + 'static/css'))                // destination path for normal CSS
        .pipe(minifyCss({                             // minify CSS
            keepSpecialComments: 0                    // remove all comments
        }))
        .pipe(rename({                                // rename file
            suffix: ".min"                            // add *.min suffix
        }))
        .pipe(gulp.dest(ui_theme_dir + 'static/css'));               // destination path for minified CSS
});


// Concatenate & minify JS (uncomment if you want to use)
/*gulp.task('concatenate', function() {
    return gulp
        .src('assets/js/*.js')                        // path to js files you want to concat
        .pipe(concat('all.js'))                       // output file name
        .pipe(gulp.dest('assets/js'))                 // destination path for normal JS
        .pipe(rename({                                // rename file
            suffix: ".min"                            // add *.min suffix
        }))
        .pipe(uglify())                               // compress JS
        .pipe(gulp.dest('assets/js'));                // destination path for minified JS
});*/


// Minify template's core JS file
gulp.task('minify_core', function() {
    return gulp
        .src(ui_theme_dir + 'static/js/core/app.js')                 // path to app.js file
        .pipe(uglify())                               // compress JS
        .pipe(rename({                                // rename file
            suffix: ".min"                            // add *.min suffix
        }))
        .pipe(gulp.dest(ui_theme_dir + 'static/js/core/'));          // destination path for minified file
});


// Watch files for changes
gulp.task('watch', function() {
    gulp.watch(ui_theme_dir + 'static/js/core/app.js', [             // listen for changes in app.js file and automatically compress
        'lint',                                       // lint
        //'concatenate',                              // concatenate & minify JS files (uncomment if in use)
        'minify_core'                                 // compress app.js
    ]); 
    gulp.watch(ui_theme_dir + 'static/less/**/*.less', ['less_full']);    // listen for changes in all LESS files and automatically re-compile
});


// Default task
gulp.task('default', [                                // list of default tasks
    'lint',                                           // lint
    'less_full',                                      // full version less compile
    //'concatenate',                                  // uncomment if in use
    'minify_core',                                    // compress app.js
    'watch'                                           // watch for changes
]);
