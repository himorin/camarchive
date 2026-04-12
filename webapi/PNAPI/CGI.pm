# -*- Mode: perl; indent-tabs-mode: nil -*-
#
# Module for CGI wrapper
#

package PNAPI::CGI;

use strict;
use lib '.';

use CGI qw(
    -no_xhtml
    :unique_headers
    :private_tempfiles
);
use base qw(CGI);
use JSON;

use PNAPI::Constants;
use PNAPI::Config;

$| = 1; # disabling output buffering
our $config;
our $out_type = "application/json"; # default to json

sub DESTROY {};

sub new {
    my ($ic, @args) = @_;
    my $class = ref($ic) || $ic;
    my $self = $class->SUPER::new(@args);

    $self->{pnapi_cookie} = [];
    $self->charset('UTF-8');

    my $err = $self->cgi_error;
    if ($err) {
        print $self->header(-status => $err);
        die "CGI PARSER ERROR: $err";
    }
    $config = new PNAPI::Config;

    return $self;
}

sub param {
    my ($self, @args) = @_;
    local $CGI::LIST_CONTEXT_WARN = 0;
    if (scalar(@args) == 1) {
        # for parameter valur request, check utf8 flag
        my @result = $self->SUPER::param(@args);
        @result = map { _fix_utf8($_) } @result;
        return wantarray ? @result : $result[0];
    }
    return $self->SUPER::param(@args);
}

sub redirect {
    my $self = pop(@_);
    return $self->SUPER::redirect(@_);
}

sub header {
    my ($self, $status, @args) = @_;
    if (! defined($status)) {$status = 200; }
    if (defined(HTTP_STATUS->{$status})) {$status = HTTP_STATUS->{$status}; }
    unshift(@args, '-status' => $status);
    unshift(@args, '-type' => $out_type);
    if (scalar(@{$self->{pnapi_cookie}})) {
        unshift(@_, '-cookie' => $self->{pnapi_cookie});
    }
    return $self->SUPER::header(@args) || "";
}

sub set_type {
    my ($self, $type) = @_;
    if (defined($type)) {$out_type = $type; }
}

sub add_cookie {
    my $self = shift;

    my %param;
    my ($key, $value);
    while ($key = shift) {
        $value = shift;
        $param{$key} = $value;
    }

    if (! (defined($param{'-name'}) && defined($param{'-value'}))) {
        return;
    }
    $param{'-path'} = $config->get('cookie_path')
        if $config->get('cookie_path'); 
    $param{'-domain'} = $config->get('cookie_domain')
        if $config->get('cookie_domain'); 
    $param{'-expires'} = $config->get('cookie_expires')
        if $config->get('cookie_expires') && 
           (! defined($param{'-expires'}));

    my @parr;
    foreach (keys(%param)) {
        unshift(@parr, $_ => $param{$_});
    }

    push(@{$self->{pnapi_cookie}}, $self->cookie(@parr));
}

sub remove_cookie {
    my $self = shift;
    my ($name) = (@_);
    $self->add_cookie('-name'    => $name,
                      '-expires' => 'Tue, 01-Jan-1980 00:00:00 GMT',
                      '-value'   => 0);
}

sub is_windows {
    my $self = shift;
    if ($self->user_agent() =~ /Windows/) {return TRUE; }
    return FALSE;
}

sub send_error {
  my ($self, $error, $message) = @_;
  print $self->header($error);
  print to_json( { 'code' => $error, 'message' => $message } );
  exit;
}

################################################################## PRIVATE

sub _fix_utf8 {
    my ($input) = @_;
    utf8::decode($input) if defined($input) && !ref($input);
    return $input;
}

1;

__END__


