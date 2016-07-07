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

##### DEPRECATED #####
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
    set help "usage:\nloader ?-options? type1 ?type2?\n  Options:\n    -h  |  -help  -->  Provides usage this text\n    -d  |  -dir  |  -directory  -->  Indicates that any arguments following this flag should be treated as directories to search in.\n        The directory list must always be followed by a -- flag to indicate the end of the directory list. the default directory is the current working directory.\n\nThe loader function is used to loader 1 or 2 files with names / file endings that end with the text inputted as the type arguments.\nWhen using loader structure files should always be listed first and trajectory files second.\nExample:\nloader pdb dcd\nThe above example would load files ending with pdb first and then files ending with dcd second."
    set usage "usage:\nloader ?-options? type1 ?type2?"
    set argCount [ llength $args ]
    if { $argCount < 1 } {
        return -code error "Wrong # of arguments:\n$usage"
    }
    set dirInit [file normalize .]
    set dirList {}
    for {set idx 0} {$idx < $argCount} {incr idx} {
        set flag [lindex $args $idx]
        switch -glob -- $flag {
            -- {
                incr idx
                break
            }
            -directory {
                while {![string match -nocase -- $flag]} {
                    incr idx
                    lappend $dirList [lindex $args $idx]
                    if {$idx == $argCount} {
                        return -code error "Missing -- flag:\n$usage"
                    }
                    
                }
                
            }
            -dir {
                while {![string match -nocase -- $flag]} {
                    incr idx
                    lappend $dirList [lindex $args $idx]
                    if {{$flag != "--"} && {$idx == $argCount}} {
                        return -code error "Missing -- flag:\n$usage"
                    }
                }
                
            }
            -d {
                while {![string match -- $flag]} {
                    if {[string match -nocase -- $flag] && $idx == [expr $argCount - 1]} {
                        return -code error "Missing -- flag:\n$usage"
                    }
                    if {[string match -- $flag]} {
                        break
                    } else {
                        incr idx
                        if {$idx == $argCount} {
                            return -code error "No -- flag encountered.\n$usage"
                        }
                        if {![string match -- $flag]} {
                            lappend $dirList [lindex $args $idx]
                        }
                    }
                }
                incr idx
                break
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
                break
            }
        }
    }
    set patList [lrange $args $idx end]
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
            set gobl [rglob . *$pat]
            foreach ent $gobl {
                lappend matches $ent
            }
        }
        if {$patCount == 1} {
            foreach match $matches {
                mol new [file normalize $match]
            }
        }
        if {$patCount == 2}  {
            for {set ida 0} {$ida < [expr [llength $matches]-1]} {incr ida} {
                set matcha [file normalize [lindex $matches $ida]]
                for {set idb [expr $ida+1]} {$idb<[llength $matches]} {incr idb} {
                    set matchb [file normalize [lindex $matches $idb]]
                    if {[file dirname $matcha] == [file dirname $matchb]} {
                        mol new $matcha waitfor all
                        puts "molid [molinfo top get id] --> $matcha"
                        mol addfile $matchb waitfor all
                    }
                }
            }
        }
    }
    if {$dirCount > 0} {
        foreach dir $dirList {
            set dir [file normalize $dir]
            if {[file isdirectory]} {
                cd $dir
                foreach pat $patList {
                    set gobl [rglob . *$pat]
                    foreach ent $gobl {
                        lappend matches $ent
                    }
                }
                if {$patCount == 1} {
                    foreach match $matches {
                        mol new [file normalize $match]
                    }
                }
                if {$patCount == 2}  {
                    for {set ida 0} {$ida < [expr [llength $matches]-1]} {incr ida} {
                        set matcha [file normalize [lindex $matches $ida]]
                        for {set idb [expr $ida+1]} {$idb<[llength $matches]} {incr idb} {
                            set matchb [file normalize [lindex $matches $idb]]
                            if {[file dirname $matcha] == [file dirname $matchb]} {
                                mol new $matcha
                                mol addfile $matchb waitfor all
                            }
                        }
                    }
                }
                cd $dirInit
            } else {
                return -code error "$dir is not a directory.\n$usage"
            }
        }
    }
}

# Marks specified tubulin monomers blue if beta and red if alpha. Requires a
# molecule ID to be inputted. Monomer arguments must be between 0 & 207.
# Usage: mtcolor molecule_id [monomer_# ...]
proc mtcolor {mid args} {
    foreach arg $args {
        if {$arg>207 || $arg<0} {
            puts "$arg out of range. Value must be between 1 and 207 inclusive."
            continue
        } else {
            set selalpha [atomselect $mid "chain A and fragment $arg"]
            set selbeta [atomselect $mid "chain B and fragment $arg"]
            if {[$selalpha num]>0} {
                mol selection "fragment $arg"
                mol representation Lines 3.0
                mol material Opaque
                mol color ColorID 1
                mol addrep $mid
            }
            if {[$selbeta num]>0} {
                mol selection "fragment $arg"
                mol representation Lines 3.0
                mol material Opaque
                mol color ColorID 0
                mol addrep $mid
            }
        }
    }
}

proc pdbdcdpullcolor {args} {
    loader pdb dcd
    set nargs [llength $args]
    set nreps [llength [molinfo list]]
    for {set n 0} {$n < $nreps} {incr n} {
        mol selection "chain A"
        mol representation Lines 3.0
        mol material Opaque
        mol color ColorID 31
        mol addrep $n

        mol selection "chain B"
        mol representation Lines 3.0
        mol material Opaque
        mol color ColorID 23
        mol addrep $n

        if {$nargs==0} {
            mtcolor $n 88 89
            continue
        }
        for {set m 0} {$m<$nargs} {incr m} {
            mtcolor $n [lindex $args $m]
        }
    }
}
