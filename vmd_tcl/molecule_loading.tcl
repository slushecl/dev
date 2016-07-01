# file: molecule_loading.tcl

# Creates a recursive glob function
# source code found here: http://wiki.tcl.tk/2042
rglob {dirlist globlist} {
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

# Finds and loads first .pdb and first .dcd file found in the indicated 
# directories and its subdirectories. If no directories are entered the
# the files are searched for starting from the current working directory.
proc load_pdb_dcd { {pdb_file ""} {dcd_file ""} } {
    if { $pdb_file=="" } {
        set pdb [lindex [rglob . *.ref.pdb] 0]
        set pdb_file $pdb
        echo $pdb_file
    }
    if { $dcd_file=="" } {
        set dcd [lindex [rglob . *.dcd] 0]
        set dcd_file $dcd
        echo $dcd_file
    }
    if {$pdb_file != "" && $dcd_file != ""} {
        mol new
        mol addfile $pdb_file
        mol addfile $dcd_file waitfor all
    }
    if {$pdb_file != "" && $dcd_file == ""} {
        mol new
        mol addfile $pdb_file
        echo "No DCD file was found so only the PDB file was loaded."
    }
}

