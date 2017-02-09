#!/usr/bin/perl -w
use strict;
use IPC::Open2;

# This scripts takes at least 2 arguments:
# - 1) the string "true" or "false" to tell us whether to *not* exclude LMDB from list of requires (ie, if argument == false, then exclude it)
# - 2) The command and it's arguments to run to auto-detect requirements (original RPM behaviour)
my $dont_exclude_tc = $ARGV[0];
my @command = @ARGV[1 .. $#ARGV];

# This will run the original find-requires script
# and then remove requirements we don't want
open2(\*IN, \*OUT, @command);
print OUT while (<STDIN>);
close(OUT);
my $list = join('', <IN>);

# Apply our exclude filters
$list =~ s/^perl\(.*?$//mg;
$list =~ s/^perl .*?$//mg;
$list =~ s/^\/opt\/rudder\/bin\/perl.*?$//mg;

$list =~ s/^.*lmdb.*?$//mg unless ($dont_exclude_tc eq "true");

print $list;
