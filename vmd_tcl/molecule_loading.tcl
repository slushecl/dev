#!/usr/bin/env tclsh
# file: molecule_loading.tcl

# Creates a recursive glob function
# source code found here: http://wiki.tcl.tk/2042
proc rglob {dirlist globlist} {
    set result {}
    set recurse {}
    foreach dir $dirlist {
        if ![file isdirectory $dir] {
            return -code error "'$dir' is not a directory"
        }
        foreach pattern $globlist {
            lappend result {*}[glob -nocomplain -directory $dir -- $pattern]
        }
        foreach file [glob -nocomplain -directory $dir -- *] {
            set file [file join $dir $file]
            if [file isdirectory $file] {
                set fileTail [file tail $file]
                if {!($fileTail eq "." || $fileTail eq "..")} {
                    lappend recurse $file
                }
            }
        }
    }
    if {[llength $recurse] > 0} {
        lappend result {*}[rglob $recurse $globlist]
    }
    return $result
}

# Finds and loads first .ref.pdb and first .dcd file found in the indicated 
# directories and its subdirectories. If no directories are entered the
# the files are searched for starting from the current working directory.
# Usage:
# load_pdb_dcd [pdb_directory | pdb_file] [dcd_directory | dcd_file]
proc load_pdb_dcd { {pdb_dir ""} {dcd_dir ""} } {
    set dir [ pwd ]
    if { $pdb_dir=="" } {
        set pdb [lindex [rglob $dir *.ref.pdb] 0]
    } else {
        set pdb [lindex [rglob $pdb_dir *.ref.pdb] 0]
    }
    cd $dir
    if { $dcd_dir=="" } {
        set dcd [lindex [rglob $dir *.dcd] 0]
    } else {
        set dcd [lindex [rglob $dcd_dir *.dcd] 0]
    }
    if { $pdb != {}  && $dcd != {} } {
        mol new
        mol addfile $pdb
        mol addfile $dcd waitfor all
        puts [ join [ list $pdb "\n" $dcd ] "" ]
    }
    if { $pdb != {} && $dcd == {} } {
        mol new
        mol addfile $pdb
        puts $pdb
        puts "No DCD file was found so only the PDB file was loaded."
    }
}

proc loader {args} {
    set help "usage:\nloader ?-options? type1 ?type2?\n  Options:\n   -h  |  -help  -->  Provides usage this text\n    -d  |  -dir  |  -directory  -->  Indicates that any arguments following this flag should be treated as directories to search in.\n        The directory list must always be followed by a -- flag to indicate the end of the directory list. the default directory is the current working directory.\n\nThe loader function is used to loader 1 or 2 files with names / file endings that end with the text inputted as the type arguments.\nExample:\nloader pdb dcd\n The above example would load files ending with pdb first and then files ending with dcd second."
    set usage "usage:\nloader ?-options? type1 ?type2?"
    set argCount [ llength $args ]
    if { $argCount < 1 } {
        return -code error "Wrong # of arguments:\n$usage"
    }
    set dirInit [pwd]
    for {set idx 0} {$idx < $argCount} {incr idx} {
        set flag [lindex $args $idx]
        switch -glob -- $flag {
            -- {
                set argList {}
                while {$idx < $argCount} {
                    incr idx
                    lappend $patList [lindex $args $idx]
                }
            }
            -directory {
                set dirList {}
                while {![glob $flag --]} {
                    incr idx
                    lappend $dirList [lindex $args $idx]
                    if {{$flag != --} && {$idx == $argCount}} {
                        return -code error "Missing -- flag:\n$usage"
                    }
                }
                incr idx -1
            }
            -dir {
                set dirList {}
                while {![glob $flag --]} {
                    incr idx
                    lappend $dirList [lindex $args $idx]
                    if {{$flag != --} && {$idx == $argCount}} {
                        return -code error "Missing -- flag:\n$usage"
                    }
                }
                incr idx -1
            }
            -d {
                set dirList {}
                while {![glob $flag --]} {
                    incr idx
                    lappend $dirList [lindex $args $idx]
                    if {{$flag != --} && {$idx == $argCount}} {
                        return -code error "Missing -- flag:\n$usage"
                    }
                }
                incr idx -1
            }
            -help {
                return -code 0 $help
            }
            -h {
                return -code 0 $help
            }
            -* {
                return -code error "Invalid flag:\n$usage"
            }
            default {
                while {$idx < $argCount} {
                    incr idx
                    lappend $patList [lindex $args $idx]
                }
            }
        }
    }
    set dirCount [llength $dirList]
    set patCount [llength $patList]
    if {$patCount < 1} {
        return -code error "No file types listed. Please indicate a file type to load.\n$usage"
    }
    if {$patCount > 2} {
        return -code error "Too many file types listed.\n$usage"
    }
    set matches {}
    if {$dirCount < 1} {
        foreach pat $patList {
            set 
        }
    }
}
#set pdb [lindex [rglob $dir *.ref.pdb] 0]
