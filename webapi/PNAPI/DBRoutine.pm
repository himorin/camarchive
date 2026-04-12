# -*- Mode: perl; indent-tabs-mode: nil -*-
#
# Module for Common DB access routines
#

package PNAPI::DBRoutine;

use strict;
use lib '.';
use PNAPI::DB;
use base qw(PNAPI::DB);

use PNAPI::Constants;

our $dbh;

sub new {
  my ($class) = @_;
  my $self = $class->SUPER::new();
  $dbh = $self->SUPER::dbh();
  return $self;
}

sub dbh {
  my ($self) = @_;
  return $dbh;
}

# sub get_text_labels {
#   my ($self, $target) = @_;
#   my $ret = {};
#   my $sth = $dbh->prepare('SELECT * FROM text_labels WHERE event_shortname = ?');
#   $sth->execute($target);
#   while (my $cur = $sth->fetchrow_hashref) {
#     if (! exists $ret->{$cur->{target}})
#       { $ret->{$cur->{target}} = {}; }
#     if (! exists $ret->{$cur->{target}}{$cur->{subid}})
#       { $ret->{$cur->{target}}{$cur->{subid}} = {}; }
#     if (! exists $ret->{$cur->{target}}{$cur->{subid}}{$cur->{subsid}})
#       { $ret->{$cur->{target}}{$cur->{subid}}{$cur->{subsid}} = {}; }
#     $ret->{$cur->{target}}{$cur->{subid}}{$cur->{subsid}}{$cur->{lang}}
#       = { "text" => $cur->{text_disp}, "comment" => $cur->{comment} };
#   }
#   return $ret;
# }
# 
# sub get_event_defs {
#   my ($self, $target) = @_;
#   my $ret = {};
#   my $sth;
#   my @tmp;
# 
#   $sth = $dbh->prepare('SELECT * FROM events WHERE event_shortname = ?');
#   $sth->execute($target);
#   if ($sth->rows != 1) { return $ret; }
#   $ret = $sth->fetchrow_hashref;
# 
#   $sth = $dbh->prepare('SELECT * FROM files WHERE uuid = ? AND confirmed = 1');
#   $sth->execute($target);
#   while (my $cur = $sth->fetchrow_hashref) {
#     $ret->{files}{$cur->{file_uuid}} = $cur;
#   }
# 
#   $sth = $dbh->prepare('SELECT * FROM event_entry WHERE event_shortname = ?');
#   $sth->execute($target);
#   while (my $cur = $sth->fetchrow_hashref) {
#     delete($cur->{event_shortname});
#     push(@tmp, $cur);
#   }
#   $ret->{entry} = \@tmp;
# 
#   $sth = $dbh->prepare('SELECT * FROM event_flags WHERE event_shortname = ?');
#   $sth->execute($target);
#   while (my $cur = $sth->fetchrow_hashref) {
#     push(@tmp, $cur->{category});
#   }
#   $ret->{flags} = \@tmp;
#   return $ret;
# }
# 
# sub get_entry_info {
#   my ($self, $eshort, $uuid) = @_;
#   my $sth;
#   my $ret;
# 
#   $sth = $dbh->prepare('SELECT * FROM entries WHERE uuid = ? AND event_shortname = ?');
#   $sth->execute($uuid, $eshort);
#   $ret = $sth->fetchrow_hashref;
#   delete($ret->{secret});
# 
#   $sth = $dbh->prepare('SELECT * FROM entry_info WHERE uuid = ?');
#   $sth->execute($uuid);
#   $ret->{'info'} = {};
#   while (my $ref = $sth->fetchrow_hashref()) {
#     if (! defined($ret->{'info'}->{$ref->{'category'}})) {
#       $ret->{'info'}->{$ref->{'category'}} = ();
#     }
#     push(@{$ret->{'info'}->{$ref->{'category'}}}, $ref->{'info'});
#   }
# 
#   $sth = $dbh->prepare('SELECT * FROM entry_flags WHERE uuid = ?');
#   $sth->execute($uuid);
#   $ret->{'flags'} = {};
#   while (my $ref = $sth->fetchrow_hashref()) {
#     $ret->{'flags'}->{$ref->{'category'}} = $ref->{'status'};
#   }
# 
#   $sth = $dbh->prepare('SELECT * FROM files WHERE uuid = ?');
#   $sth->execute($uuid);
#   $ret->{'files'} = [];
#   while (my $cur = $sth->fetchrow_hashref) {
#     delete($cur->{'uuid'});
#     push(@{$ret->{'files'}}, $cur);
#   }
# 
#   $sth = $dbh->prepare('SELECT * FROM menus WHERE uuid = ?');
#   $sth->execute($uuid);
#   $ret->{'menus'} = ();
#   while (my $cur = $sth->fetchrow_hashref) {
#     delete($cur->{'uuid'});
#     push(@{$ret->{'menus'}}, $cur);
#   }
# 
#   $sth = $dbh->prepare('SELECT * FROM entry_verify WHERE uuid = ?');
#   $sth->execute($uuid);
#   $ret->{'email_verify'} = {};
#   while (my $cur = $sth->fetchrow_hashref) {
#     $ret->{'email_verify'}->{$cur->{'email'}} = $cur->{'status'};
#   }
# 
#   return $ret;
# }
# 
# 


1;

__END__

