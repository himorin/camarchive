# -*- Mode: perl; indent-tabs-mode: nil -*-
#
# Module for Template wrapper and sending email
#

# template file: <lang>/<ID>.tmpl

package PNAPI::Template;

use utf8;
use strict;

use base qw(Exporter);
use lib '.';
use File::Basename qw(basename dirname);
use Template;
use Email::Sender::Simple;
use Email::MIME;
use Encode;

use PNAPI::Constants;
use PNAPI::Config;

%PNAPI::Template::EXPORT = qw(
  new
  process
  set_vars
  update_lang

  send_email
);

our $o_config;
our $c_template;
our %h_vars = {};

sub new {
  my ($self) = @_;
  $o_config = new PNAPI::Config();
  $c_template = {
    INCLUDE_PATH  => PNAPI::Constants::LOCATIONS->{'template'} . '/' . PNAPI::Constants::DEF_LANG . '/',
    INTERPOLATE   => 1,
    PRE_CHOMP     => 0,
    POST_CHOMP    => 0,
    EVAL_PERL     => 0,
    COMPILE_DIR   => PNAPI::Constants::LOCATIONS->{'datacache'},
#    DEBUG         => 'parser, under',
    ENCODING      => 'UTF-8',
    PRE_PROCESS   => 'initialize.none.tmpl',
    FILTERS       => {
      email_header => \&PNAPI::Template::_filter_email_header,
    },
    CONSTANTS     => _load_constants(),
    VARIABLES     => {
    },
  };
  return $self;
}

sub process {
  my ($self, $template, $cur_vars, $out) = @_;
  my $o_tmpl = Template->new($c_template);
  if (defined($cur_vars)) {
    foreach (keys(%$cur_vars)) {
      $self->set_vars($_, $cur_vars->{$_});
    }
  }
  $template .= '.tmpl';
  $o_tmpl->process($template, \%h_vars, $out);
}

sub set_vars {
  my ($self, $name, $value) = @_;
  $h_vars{$name} = $value;
}

sub update_lang {
  my ($self, $lang) = @_;
  $c_template->{INCLUDE_PATH} = PNAPI::Constants::LOCATIONS->{'template'} . '/' . $lang . '/';
}

sub send_email {
  my ($self, $tmpl, $is_admin, $to, $vars, $secret, $lang) = @_;
  my $out;
  my $ref = {};
  $ref->{emailto} = $to;
  $ref->{siteadmin} = $o_config->get('site_email');
  $ref->{vars} = $vars;
  $ref->{params} = $o_config->get_hash();
  $ref->{secret} = $secret;
  if ($is_admin) {
    $self->update_lang(PNAPI::Constants::DEF_LANG);
  } elsif (defined($lang)) {
    $self->update_lang($lang);
  }
  $self->process($tmpl, $ref, \$out);
  my $emp = Email::MIME->new($out);
  return Email::Sender::Simple->send($emp);
}

###---------

sub _load_constants() {
  my %consts;
  foreach my $item (@PNAPI::Constants::EXPORT) {
    if (ref PNAPI::Constants->$item) {
      $consts{$item} = PNAPI::Constants->$item;
    } else {
      my @list = (PNAPI::Constants->$item);
      $consts{$item} = (scalar(@list) == 1) ? $list[0] : \@list;
    }
  }
  return \%consts;
}

sub _filter_email_header {
  my ($var) = @_;
  return Encode::encode('MIME-Header', $var);
}



1;

__END__
