
from docutils import nodes
from docutils.parsers.rst import Directive, directives

from sphinx import addnodes
from sphinx.locale import l_
from sphinx.domains import Domain, ObjType
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode
from sphinx.util.docfields import Field, GroupedField, TypedField
from sphinx.util.docfields import DocFieldTransformer
from sphinx.directives import ObjectDescription
from sphinx.locale import l_, _
import javasphinx.formatter as formatter
import re


rust_struct_sig_re = re.compile(r'''^(?P<mods>(?P<pub>.*pub)?)\sstruct\s(?P<name>[\w]+)$''', re.VERBOSE)
rust_function_sig_re = re.compile(r'''^(?P<mods>(?P<pub>.*pub)?)?\s?fn\s(?P<name>[\w]+)[(](?P<args>.*)[)](\s[-][>]\s(?P<return>.+))?\s*$''', re.VERBOSE)
rust_arg_re = re.compile(r'''^(?P<var>\w+)[\s:]*(?P<type>\w+)$''', re.VERBOSE)

class RustXRefRole(XRefRole):
    def process_link(self, env, refnode, has_explicit_title, title, target):
        if not has_explicit_title:
            target = target.lstrip('~')  # only has a meaning for the title
            # if the first character is a tilde, don't display the module/class
            # parts of the contents
            if title[0:1] == '~':
                title = title[1:]
                dot = title.rfind('.')
                if dot != -1:
                    title = title[dot+1:]
            return title, target


class RustUse(Directive):
    """
    This directive is to tell Sphinx the source of a referenced object
    """

    pass

class RustObject(ObjectDescription):
    """
    Description of a Rust language object.
    """

    option_spec = {
        'noindex': directives.flag,
        'crate': directives.unchanged,
        'impl': directives.unchanged
    }

    def get_crate(self):
        return self.options.get('crate', self.env.temp_data.get('rust:crate'))

    def get_module(self):
        return None

    def get_implementation(self):
        pass

    def get_index_text(self, crate, module, impl, name):
        """
        Get the text for this object that goes in the index
        """
        raise NotImplementedError

    def handle_signature(self, sig, signode):
        """
        handle the signature of the directive
        """
        raise NotImplementedError

    def add_target_and_index(self, name, sig, signode):
        crate = self.get_crate()
        module = self.get_module()

        fullname = "::".join(filter(None, (crate, module, name)))
        basename = fullname.partition('(')[0]

        print("Fullname", fullname)
        print("Basename", basename)
        print("SIG", sig)

        indextext = self.get_index_text(crate, None, None, basename)
        if indextext:
            self.indexnode['entries'].append(_create_indexnode(indextext, fullname))



class RustFunction(RustObject):
    """
    Description of a rust function
    """

    doc_field_types = [
        TypedField('parameter', label=l_('Parameters'),
                   names=('param', 'parameter', 'arg', 'argument'),
                   typerolename='type', typenames=('type',)),
        Field('returnvalue', label=l_('Returns'), has_arg=False,
              names=('returns', 'return'))
    ]

    def get_index_text(self, crate, module, impl, name):
        """
        Get the text for this object that goes in the index
        """
        return _('%s (Rust function)') % name

    def handle_signature(self, sig, signode):
        """
        handle the signature of the directive
        """
        print("handling struct signature: ", sig)

        sig_match = rust_function_sig_re.match(sig)
        name = sig_match.group("name")
        mods = sig_match.group("mods")

        formatted_mods = formatter.output_modifiers(mods).build()
        signode += nodes.Text(mods + ' ', mods + ' ')
        signode += nodes.Text('fn ', 'fn ')

        signode += addnodes.desc_name(name, name)

        return name

class RustTrait(RustObject):
    def get_index_text(self, crate, module, impl, name):
        return _('%s (Rust trait)') % name


class RustStruct(RustObject):
    """
    Description of a rust struct
    """

    doc_field_types = [
        GroupedField('parameter', names=('param',), label=l_('Parameters'))
    ]

    def get_index_text(self, crate, module, impl, name):
        """
        Get the text for this object that goes in the index
        """
        return _('%s (Rust struct)') % name

    def handle_signature(self, sig, signode):
        """
        handle the signature of the directive
        """
        print("handling struct signature: ", sig)

        sig_match = rust_struct_sig_re.match(sig)
        name = sig_match.group("name")
        mods = sig_match.group("mods")

        formatted_mods = formatter.output_modifiers(mods).build()
        signode += nodes.Text(mods + ' ', mods + ' ')
        signode += nodes.Text('struct ', 'struct ')

        signode += addnodes.desc_name(name, name)

        return name


class RustMember(RustObject):
    def get_index_text(self, crate, module, impl, name):
        return _('%s (Rust member)') % name


class RustEnum(RustObject):
    def get_index_text(self, crate, module, impl, name):
        return _('%s (Rust enum)') % name

class RustImplementation(RustObject):
    def get_index_text(self, crate, module, impl, name):
        return _('%s (Rust implementation)') % name

class RustCrate(Directive):
    """
    Directive to mark description of a new crate
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False

    option_spec = {
        'noindex': directives.flag
    }

    def run(self):
        env = self.state.document.settings.env
        crate = self.arguments[0].strip()
        noindex = 'noindex' in self.options
        env.temp_data['java:crate'] = crate
        env.domaindata['rust']['objects'][crate] = (env.docname, 'crate', crate)
        ret = []

        if not noindex:
            targetnode = nodes.target('', '', ids=['crate-' + crate], ismod=True)
            self.state.document.note_explicit_target(targetnode)

            # the platform and synopsis aren't printed; in fact, they are only
            # used in the modindex currently
            ret.append(targetnode)

            indextext = _('%s (crate)') % (crate,)
            inode = addnodes.index(entries=[_create_indexnode(indextext, 'crate-' + crate)])
            ret.append(inode)

        return ret

class RustModule(Directive):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False

    option_spec = {
        'noindex': directives.flag
    }

    def run(self):
        env = self.state.document.settings.env
        module = self.arguments[0].strip()
        noindex = 'noindex' in self.options
        env.temp_data['java:module'] = module
        env.domaindata['rust']['objects'][module] = (env.docname, 'module', module)
        ret = []

        if not noindex:
            targetnode = nodes.target('', '', ids=['module-' + module], ismod=True)
            self.state.document.note_explicit_target(targetnode)

            # the platform and synopsis aren't printed; in fact, they are only
            # used in the modindex currently
            ret.append(targetnode)

            indextext = _('%s (module)') % (module,)
            inode = addnodes.index(entries=[_create_indexnode(indextext, 'module-' + module)])
            ret.append(inode)

        return ret

class RustDomain(Domain):
    """
    Rust language domain.
    """

    name = 'rust'
    label = "Rust"
    object_types = {
        'function': ObjType(l_('function'), 'fn'),
        'struct': ObjType(l_('struct'), 'struct'),
        'trait': ObjType(l_('trait'), 'trait'),
        'enum': ObjType(l_('enum'), 'enum'),
        'member': ObjType(l_('member'), 'member'),
        'implementation': ObjType(l_('implementation'), 'impl'),
    }

    directives = {
        'function': RustFunction,
        'struct': RustStruct,
        'trait': RustTrait,
        'enum': RustEnum,
        'member': RustMember,
        'crate': RustCrate,
        'module': RustModule,
        'implementation': RustImplementation,
        'use': RustUse
    }

    roles = {
        'any': RustXRefRole(),
        'struct': RustXRefRole(),
        'trait': RustXRefRole(),
        'member': RustXRefRole(),
        'crate': RustXRefRole(),
        'module': RustXRefRole(),
        'ref': RustXRefRole()
    }

    initial_data = {
        'objects': {},  # fullname -> docname, objtype, basename
    }

    def resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode):
        objects = self.data['objects']
        module = node.get('rust:module')

        # Partial function to make building the response easier
        make_ref = lambda fullname: make_refnode(builder, fromdocname, objects[fullname][0], fullname, contnode, fullname)

        if target in objects:
            return make_ref(target)

    def get_objects(self):
        for refname, (docname, type, _) in self.data['objects'].items():
            yield (refname, refname, type, docname, refname, 1)




def _create_indexnode(indextext, fullname):
    # See https://github.com/sphinx-doc/sphinx/issues/2673
    # if version_info < (1, 4):
    #     return ('single', indextext, fullname, '')
    # else:
    return ('single', indextext, fullname, '', None)