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
    if { $pdb_dir=="" } {
        set pdb [lindex [rglob . *.ref.pdb] 0]
    } else {
        set pdb [lindex [rglob $pdb_dir *.ref.pdb] 0]
    }
    if { $dcd_dir=="" } {
        set dcd [lindex [rglob . *.dcd] 0]
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
