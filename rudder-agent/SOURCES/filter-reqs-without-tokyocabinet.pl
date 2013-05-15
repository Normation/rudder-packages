#!/usr/bin/perl -w
use strict;
use IPC::Open2;

# This will run the original find-requires script
# and then remove requirements we don't want
open2(\*IN, \*OUT, @ARGV);
print OUT while (<STDIN>);
close(OUT);
my $list = join('', <IN>);

# Apply our exclude filters
$list =~ s/^perl\(.*?$//mg;
$list =~ s/^perl .*?$//mg;
$list =~ s/^\/opt\/rudder\/bin\/perl.*?$//mg;
$list =~ s/^.*tokyocabinet.*?$//mg;

print $list;
