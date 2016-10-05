# mt_coloring.tcl

package provide mt 1.0
namespace eval ::mt {
  #RecursiveSearch declarations

#  variable pat
#  variable initDir
#  variable dirList {}
  #fileLoader declarations
#  variable args
  #fragColorizer declarations
#  variable molid 0
#  variable args

  namespace export fragColorizer
  namespace export fileLoader
  namespace export mtLoader
  namespace export mtColorizer
  namespace export ArgParser
  namespace export smoother
}

proc ::mt::RecursiveSearch {initDir pat} {
  variable dirs
  variable parents
  variable children
  variable parent
  variable length
  variable child
  variable dir
  variable i
  variable result
  set initDir [string trimright [file join [file normalize $initDir] { }]]
  set dirs [list $initDir]
  set parents $initDir
  while {[llength $parents] > 0} {
    set children [list]
    foreach parent $parents {
      set children [concat $children [glob -nocomplain -type {d r} -path $parent *]]
    }
    set length [llength $children]
    for {set i 0} {$i < $length} {incr i} {
      lset children $i [string trimright [file join [file normalize [lindex $children $i]] { }]]
    }
    set children [lsort -unique $children]
    set parents [list]
    foreach child $children {
      if {[lsearch -sorted $dirs $child] == -1} {
        lappend parents $child
      }
    }
    set dirs [lsort -unique [concat $dirs $parents]]
  }
  set result [list]
  foreach dir $dirs {
    set result [concat $result [glob -nocomplain -type {f r} -path $dir -- *$pat]]
  }
  set length [llength $result]
  for {set i 0} {$i < $length} {incr i} {
    lset result $i [file normalize [lindex $result $i]]
  }
  return [lsort -unique $result]
}

proc ::mt::fileLoader {args} {
  variable usage
  variable help
  variable argCount [llength $args]
  variable dirInit [file normalize .]
  variable dirList {}
  variable idx
  variable flag
  variable patList
  variable dirCount
  variable patCount
  variable matches [list]
  variable pat
  variable match
  variable ida
  variable idb
  variable matcha
  variable matchb
  variable matchCount0 0
  variable matchCount 0
#  if {{fileLoader} in [namespace import]} {
#    set usage "usage:\nfileLoader ?-h || -d dirlist --? Type1 ?Type2?"
#  } else {
  set usage "usage:\nfileLoader ?-h || -d dirlist --? Type1 ?Type2?"
#  }
  set help "$usage

options:
    -h  |  -help                --> Provides usage this text.
    -d  |  -dir  |  -directory  --> Indicates that any arguments following
                                    this flag are directories to search in.
                                    The directory list must always be followed
                                    by a -- flag to indicate the end of the
                                    directory list. the default directory is
                                    the current working directory.

The loader function is used to loader 1 or 2 files with names / file endings
that end with the text inputted as the type arguments.  When using loader
structure files should always be listed first and trajectory files second.

Example:
--> fileLoader .pdb .dcd
    The above example would load files ending with pdb first and then files
    ending with dcd second."
  if {$argCount < 1} {
    return -code error "Too few arguments."
  }
  for {set idx 0} {$idx < $argCount} {incr idx} {
    set flag [lindex $args $idx]
    switch -glob -- $flag {
      -- {
        incr idx
        break
      }
      -d {
        while {![string match "--" [lindex $args $idx]]} {
          incr idx
          if {[string match "--" [lindex $args $idx]] && $idx == $argCount} {
            return -code error "No file types indicated."
          }
          if {[string match "--" [lindex $args $idx]]} {
            break
          }
          if {$idx == $argCount && ![string match "--" [lindex $args $idx]]} {
            return -code error "No -- flag encountered."
          }
          if {![string match "--" [lindex $args $idx]]} {
            set dirList [join [list $dirList [lindex $args $idx]]]
          }
        }
        incr idx
        break
      }
      -h {
        return -code 0 $help
      }
      -* {
        return -code error "Invalid flag."
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
    return -code error "No file types listed."
  }
  if {$patCount > 2} {
    return -code error "Too many file types listed."
  }
  if {$dirCount <= 0} {
    foreach pat $patList {
      set matchCount0 [llength $matches]
      set matches [concat $matches [eval ::mt::RecursiveSearch . $pat]]
      set matchCount [llength $matches]
      if {$matchCount - $matchCount0 == 0} {
        puts "The pattern '$pat' could not be matched."
        set patCount [expr $patCount - 1]
      }
    }
  }
  if {$dirCount >= 1} {
    foreach pat $patList {
      # Length of the matches list before matching a given pattern
      set matchCount0 [llength $matches]
      foreach dir $dirList {
        set matches [concat $matches [eval ::mt::RecursiveSearch $dir $pat]]
      }
      # Length of the matches list after matching a given pattern
      set matchCount [llength $matches]
      if {$matchCount - $matchCount0 == 0} {
        puts "The pattern '$pat' could not be matched."
        set patCount [expr $patCount - 1]
      }
    }
  }
  if {$patCount == 0} {
    return -code error "No files matching '[join $patList {' or '}]' could be found."
  }
  if {$patCount == 1} {
    foreach match $matches {
      mol new [file normalize $match]
      puts "molid [molinfo top get id] --> $match"
    }
  }
  if {$patCount == 2} {
    for {set ida 0} {$ida < [expr [llength $matches] - 1]} {incr ida} {
      set matcha [file normalize [lindex $matches $ida]]
      for {set idb [expr $ida + 1]} {$idb < [llength $matches]} {incr idb} {
        set matchb [file normalize [lindex $matches $idb]]
        if {[string match -nocase \
              [file dirname $matcha]* [file dirname $matchb]] == 1 || \
             [string match -nocase \
               [file dirname $matchb]* [file dirname $matcha]] == 1 \
           } then {
          mol new $matcha waitfor all
          mol addfile $matchb waitfor all
          puts "molid [molinfo top get id] --> $matcha"
          puts "molid [molinfo top get id] --> $matchb"
        }
      }
    }
  }
}

proc ::mt::fragColorizer {molid args} {
  variable selAlpha
  variable selBeta
  variable arg
  foreach arg $args {
    if {$arg>207 || $arg<0} {
      continue
    } else {
      set selAlpha [atomselect $molid "chain A and fragment $arg"]
      set selBeta [atomselect $molid "chain B and fragment $arg"]
      if {[$selAlpha num]>0} {
        mol selection "fragment $arg"
        mol representation Lines 3.0
        mol material Opaque
        mol color ColorID 1
        mol addrep $molid
      }
      if {[$selBeta num]>0} {
        mol selection "fragment $arg"
        mol representation Lines 3.0
        mol material Opaque
        mol color ColorID 0
        mol addrep $molid
      }
    }
  }
}

proc ::mt::mtColorizer {args} {
  variable argsCount [llength $args]
  variable molidList
  variable molid
  if {$argsCount < 1} {
    set molidList [molinfo list]
  } else {
    set molidList $args
  }
  foreach molid $molidList {
    mol selection "chain A"
    mol representation Lines 3.0
    mol material Opaque
    mol color ColorID 31
    mol addrep $molid

    mol selection "chain B"
    mol representation Lines 3.0
    mol material Opaque
    mol color ColorID 23
    mol addrep $molid
  }
}

proc ::mt::mtLoader {args} {
  # Variable Declaration
  variable argsCount [llength $args]
  variable arg
  variable dirList [list [string trimright [file join [file normalize .] { }]]]
  variable typeList [list .ref.pdb .dcd]
  variable type
  variable fragList [list 88 89]
  variable molid
  variable globIndexList [list]
  variable globIndex
  variable exactIndex
  # Argument Parsing
  foreach arg $args {
    if {[string is integer -strict $arg] && $arg >= 0 && $arg <= 207} {
      set fragList [join [list $fragList $arg]]
    } elseif {[string is integer -strict $arg]} {
      puts "'$arg' is out of range."
    } elseif {[file isdirectory [string trimright [file join [file normalize $arg] { }]]]} {
      set dirList [join [list $dirList [string trimright [file join [file normalize $arg] { }]]]]
    } elseif {[string match */* $arg]} {
      puts "'$arg' is not a valid directory."
    } elseif {[regexp {[[:alpha:]]+} $arg] && [string match *.* $arg]} {
      set typeList [join [list $typeList $arg]]
    } elseif {[regexp {[[:alpha:]]+} $arg]} {
      set typeList [join [list $typeList [join [list {.*} $arg] ""]]]
    } elseif {[string is space -strict $arg]} {
      puts "'$arg' is whitespace. Whitespace is not valid input."
    } elseif {[regexp {\d+} $arg]} {
      puts "'$arg' is a non-integer. Non-integers are not valid input"
    } elseif {[string is list -strict $arg] == 1} {
      puts "'$arg' is a list. Lists are not valid input."
    } else {
      puts "'$arg' is not valid input."
    }
  }
  set dirList [lsort -unique $dirList]
  set typeList [lsort -unique -decreasing $typeList]
  set fragList [lsort -unique $fragList]
  if {[llength $dirList] > 1} {
    set exactIndex [lsearch $dirList [string trimright [file join [file normalize .] { }]]]
    set dirList [lreplace $dirList $exactIndex $exactIndex]
  }
  if {[llength $typeList] > 2} {
    set exactIndex [lsearch -exact $typeList .ref.pdb]
    set typeList [lreplace $typeList $exactIndex $exactIndex]
    set exactIndex [lsearch -exact $typeList .dcd]
    set typeList [lreplace $typeList $exactIndex $exactIndex]
  }
  if {[llength $fragList] > 2} {
    set exactIndex [lsearch -exact $fragList 88]
    set fragList [lreplace $fragList $exactIndex $exactIndex]
    set exactIndex [lsearch -exact $fragList 89]
    set fragList [lreplace $fragList $exactIndex $exactIndex]
  }
  foreach type $typeList {
    set globIndexList [lsearch -all $typeList $type]
    set exactIndex [lsearch -exact $typeList $type]
    foreach globIndex $globIndexList {
      if {$globIndex != $exactIndex} {
        set typeList [lreplace $typeList $globIndex $globIndex]
      }
    }
  }
  foreach dir $dirList {
    set globIndexList [lsearch -all $dirList $dir*]
    set exactIndex [lsearch -exact $dirList $dir]
    foreach globIndex $globIndexList {
      if {$globIndex != $exactIndex} {
        set dirList [lreplace $dirList $globIndex $globIndex]
      }
    }
  }
  puts "$dirList\n$typeList\n$fragList"
  # Process Body
  eval ::mt::fileLoader -d $dirList -- $typeList
  eval ::mt::mtColorizer
  foreach molid [molinfo list] {
    eval ::mt::fragColorizer $molid $fragList
  }
}

proc ::mt::smoother {args} {
  foreach mol [molinfo list] {
    for {set idrep 0} {$idrep < [molinfo $mol get numreps]} {incr idrep} {
      mol smoothrep $mol $idrep 5
    }
  }
}

proc ::mt::ArgParser {args} {
  variable argCount [llength $args]
  variable idx
  variable flag
  variable intList [list]
  variable dirList [list]
  variable fileList [list]
  variable strList [list]
  variable numList [list]
  variable listList [list]
  variable boolList [list]
  variable boolArray
  array set boolArray {
    intBool false
    dirBool false
    strBool false
    numBool false
    fileBool false
    listBool false
    boolBool false
  }
  for {set idx 0} {$idx < $argCount} {incr idx} {
    set flag [lindex $args $idx]
    switch -glob -- $flag {
      -- {
        break
      }
      -i* {
        set boolArray(intBool) true
      }
      -d* {
        set boolArray(dirBool) true
      }
      -f* {
        set boolArray(fileBool) true
      }
      -s* {
        set boolArray(strBool) true
      }
      -n* {
        set boolArray(numBool) true
      }
      -l* {
        set boolArray(listBool) true
      }
      -b* {
        set boolArray(boolBool) true
      }
      default {
        break
      }
    }
  }
  for {set idx $idx} {$idx < $argCount} {incr idx} {
    if {[string is integer -strict $arg]} {
      set intList [join [list $intList $arg]]
    } elseif {[file isdirectory [string trimright [file join [file normalize $arg] { }]]]} {
      set dirList [join [list $dirList [string trimright [file join [file normalize $arg] { }]]]]
      #  } elseif {[string match */* $arg]} {
      #  puts "'$arg' is not a valid directory."
    } elseif{[file isfile [string trimright [file join [file normalize $arg] { }]]]} {
      set fileList [join [list $fileList[ string trimright [file join [ file normalize $arg] { }]]]]
      #  } elseif {[regexp {[[:alpha:]]+} $arg] && [string match *.* $arg]} {
      #    set typeList [join [list $typeList $arg]]
    } elseif {[regexp {\d+} $arg]} {
      set numList [join [list $numList $arg]]
    } elseif {[string is boolean -strict $arg]} {
      set boolList [join [list $numList $arg]]
    } elseif {[regexp {[[:alpha:]]+} $arg]} {
      set strList [join [list $typeList [join [list {.*} $arg] ""]]]
    } elseif {[string is space -strict $arg]} {
      puts "'$arg' is whitespace. Whitespace is not valid input."

    } elseif {[string is list -strict $arg] == 1} {
      set listList [join [list $listList $arg]]
    } else {
      puts "'$arg' is not valid input."
    }
  }
  foreach bool [array names boolArray] {
    if {$boolArray($bool)} {
      switch -glob -- $bool {
        i* {
          return $intList
        }
        d* {
          return $dirList
        }
        f* {
          return $fileList
        }
        s* {
          return $strList
        }
        n* {
          return $numList
        }
        l* {
          return $listList
        }
        b* {
          return $boolList
        }
      }
    }
  }
}
