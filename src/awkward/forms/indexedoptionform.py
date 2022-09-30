# BSD 3-Clause License; see https://github.com/scikit-hep/awkward-1.0/blob/main/LICENSE

import awkward as ak
from awkward.forms.form import Form, _parameters_equal


class IndexedOptionForm(Form):
    is_OptionType = True
    is_IndexedType = True

    def __init__(
        self,
        index,
        content,
        has_identifier=False,
        parameters=None,
        form_key=None,
    ):
        if not ak._util.isstr(index):
            raise ak._errors.wrap_error(
                TypeError(
                    "{} 'index' must be of type str, not {}".format(
                        type(self).__name__, repr(index)
                    )
                )
            )
        if not isinstance(content, Form):
            raise ak._errors.wrap_error(
                TypeError(
                    "{} all 'contents' must be Form subclasses, not {}".format(
                        type(self).__name__, repr(content)
                    )
                )
            )

        self._index = index
        self._content = content
        self._init(has_identifier, parameters, form_key)

    @property
    def index(self):
        return self._index

    @property
    def content(self):
        return self._content

    def __repr__(self):
        args = [repr(self._index), repr(self._content)] + self._repr_args()
        return "{}({})".format(type(self).__name__, ", ".join(args))

    def _to_dict_part(self, verbose, toplevel):
        return self._to_dict_extra(
            {
                "class": "IndexedOptionArray",
                "index": self._index,
                "content": self._content._to_dict_part(verbose, toplevel=False),
            },
            verbose,
        )

    def _type(self, typestrs):
        if self.parameter("__array__") == "categorical":
            parameters = dict(self._parameters)
            del parameters["__array__"]
            parameters["__categorical__"] = True
        else:
            parameters = self._parameters

        return ak.types.OptionType(
            self._content._type(typestrs),
            parameters,
            ak._util.gettypestr(self._parameters, typestrs),
        ).simplify_option_union()

    def __eq__(self, other):
        if isinstance(other, IndexedOptionForm):
            return (
                self._has_identifier == other._has_identifier
                and self._form_key == other._form_key
                and self._index == other._index
                and _parameters_equal(
                    self._parameters, other._parameters, only_array_record=True
                )
                and self._content == other._content
            )
        else:
            return False

    def simplify_optiontype(self):
        if isinstance(
            self._content,
            (
                ak.forms.IndexedForm,
                ak.forms.IndexedOptionForm,
                ak.forms.ByteMaskedForm,
                ak.forms.BitMaskedForm,
                ak.forms.UnmaskedForm,
            ),
        ):
            return ak.forms.IndexedOptionForm(
                "i64",
                self._content.content,
                has_identifier=self._has_identifier,
                parameters=self._parameters,
            ).simplify_optiontype()
        else:
            return self

    def purelist_parameter(self, key):
        if self._parameters is None or key not in self._parameters:
            return self._content.purelist_parameter(key)
        else:
            return self._parameters[key]

    @property
    def purelist_isregular(self):
        return self._content.purelist_isregular

    @property
    def purelist_depth(self):
        return self._content.purelist_depth

    @property
    def is_identity_like(self):
        return self._content.is_identity_like

    @property
    def minmax_depth(self):
        return self._content.minmax_depth

    @property
    def branch_depth(self):
        return self._content.branch_depth

    @property
    def fields(self):
        return self._content.fields

    @property
    def is_tuple(self):
        return self._content.is_tuple

    @property
    def dimension_optiontype(self):
        return True

    def _columns(self, path, output, list_indicator):
        self._content._columns(path, output, list_indicator)

    def _select_columns(self, index, specifier, matches, output):
        return IndexedOptionForm(
            self._index,
            self._content._select_columns(index, specifier, matches, output),
            self._has_identifier,
            self._parameters,
            self._form_key,
        )

    def _column_types(self):
        return self._content._column_types()