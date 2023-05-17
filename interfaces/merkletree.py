from __future__ import annotations
from .common import (
    ImplementationError,
    TestCase,
    RaisesError,
    tressa,
    eton,
    get_notes,
    clear_notes,
    error,
    get_errors,
    clear_errors
)
from random import randint
from typing import Any, Protocol, runtime_checkable
import hashlib
import traceback


"""
    This interface specifies the required behaviors of a Merkle tree
    implementation. A Merkle tree implementation must have the following:
    - a set_hash_function for setting the hash function
    - a get_hash_function for getting the hash function
    - a class implementing the MerkleTreeProtocol

    A Merkle tree implementation should have the following:
    - error messages that match those specified below any `with RaisesError` clauses
    - multiple error types to distinguish between a usage error and a security error
    - test suite for any additional features and potential security attacks

    The check_module function will test all must-have requirements and
    make note of any discrepancies it finds for the should-have criteria.
"""


@runtime_checkable
class MerkleTreeProtocol(Protocol):
    """Duck-type protocol for the Tree class."""
    def __init__(self, left: Any, right: Any) -> None:
        """Set the left, right, and calculated root."""
        ...

    def __str__(self) -> str:
        """Return the root, left, and right in hexadecimal."""
        ...

    def __repr__(self) -> str:
        """Return the root, left, and right in hexadecimal recursively."""
        ...

    def to_dict(self) -> dict:
        """Serialize to a dict."""
        ...

    @classmethod
    def from_leaves(cls, leaves: list[bytes]) -> MerkleTreeProtocol:
        """Return a full Tree constructed from the leaves."""
        ...

    @classmethod
    def from_dict(cls, data: dict) -> MerkleTreeProtocol:
        """Deserialize from a dict and return an instance."""
        ...

    def prove(self, leaf: bytes, verbose: bool = False) -> dict:
        """Create an inclusion proof for a leaf. Use verbose=True to add
            hash checks at each tree level.
        """
        ...

    @staticmethod
    def verify(root: bytes, leaf: bytes) -> None:
        """Verify an inclusion proof is valid. Throws AssertionError upon
            failure on any step or on invalid input.
        """
        ...


def check_module(module, implementation_map: dict) -> None:
    """Checks the whole module."""
    # reset
    clear_errors()
    clear_notes()

    # basic checks
    tressa(type(module) is type(hashlib), 'module must be a module')
    tressa('set_hash_function' in dir(module), 'module missing set_hash_function')
    tressa('get_hash_function' in dir(module), 'module missing get_hash_function')
    tressa(type(implementation_map) is dict,
        'implementation_map must be dict mapping implementation classes from the module to protocols')

    # test get_hash_function and set_hash_function
    try:
        original_hash_function = module.get_hash_function()
        tressa(callable(original_hash_function), 'get_hash_function returned non-callable')
    except BaseException as e:
        raise ImplementationError(f'get_hash_function failed: {e}')

    try:
        new_hash_function = lambda preimage: hashlib.sha256(preimage).digest()
        module.set_hash_function(new_hash_function)
        tressa(module.get_hash_function() == new_hash_function,
            'set_hash_function failed to set new hash function')
    except BaseException as e:
        raise ImplementationError(f'set_hash_function failed: {e}')

    for key, value in implementation_map.items():
        try:
            tressa(type(key) is type,
                'implementation_map must be dict mapping implementation classes to protocols')
            tressa(issubclass(value, Protocol),
                'implementation_map must be dict mapping implementation classes to protocols')
            check_implementation(key, value)
        except BaseException as e:
            if e.__traceback__:
                error(False, f'{e}: {traceback.format_exc()}')
            else:
                error(False, f'{e}')

    for err in get_errors():
        print(f'error: {err}')

    for nt in get_notes():
        print(f'note: {nt}')


def check_implementation(implementation, protocol) -> None:
    """Checks the implementation of the protocol."""
    if protocol is MerkleTreeProtocol:
        check_implementation_of_MerkleTreeProtocol(implementation)


def check_implementation_of_MerkleTreeProtocol(implementation):
    """Checks the implementation of the MerkleTreeProtocol interface."""
    with TestCase('basic checks'):
        assert type(implementation) is type, 'implementation must be a class'

        try:
            instance = implementation(left=b'left', right=b'right')
        except BaseException as e:
            assert False, f'initialization failed: {e}'

        instance = implementation(left=b'left', right=b'right')
        assert isinstance(instance, MerkleTreeProtocol), \
            'implementaiton does not implement the interface'

    with TestCase('joins left and right into root'):
        left = hashlib.sha256(b'left').digest()
        right = hashlib.sha256(b'right').digest()
        joined = hashlib.sha256(left + right).digest()
        instance = implementation(left=left, right=right)
        assert hasattr(instance, 'root'), 'instance must have accessible root'
        assert type(instance.root) is bytes, 'instance.root must be bytes'
        assert instance.root == joined, 'instance.root incorrect hash value'

    with TestCase('from_leaves hashes and joins leaves'):
        leaves = [b'one', b'two', b'three']
        hashes = [hashlib.sha256(l).digest() for l in leaves]
        left = hashlib.sha256(hashes[0] + hashes[1]).digest()
        right = hashes[-1]
        root = hashlib.sha256(left + right).digest()
        instance = implementation.from_leaves(leaves)
        assert hasattr(instance, 'left'), 'instance must have accessible left'
        assert type(instance.left) is implementation, 'instance.left incorrect value'
        assert instance.left.root == left, 'instance.left.root incorrect value'
        assert hasattr(instance, 'right'), 'instance must have accessible right'
        assert instance.right == right, 'instance.right incorrect value'
        assert instance.root == root, 'instance.root incorrect hash value'

    with TestCase('from_leaves with <2 leaves raises error'):
        with RaisesError('from_leaves with only one leaf should raise an error') as e:
            implementation.from_leaves([b'just one leaf'])
        eton(str(e.exception) == 'must have at least 2 leaves',
            f'{e.label}: incorrect error message')

    with TestCase('from_leaves joins any number of leaves'):
        roots = set()
        for i in range(2, 300):
            leaves = [n.to_bytes(2, 'big') for n in range(i)]
            instance = implementation.from_leaves(leaves)
            assert instance.root not in roots
            roots.add(instance.root)

    with TestCase('instance.to_dict serializes to a dict'):
        instance = implementation(b'left', b'right')
        assert hasattr(instance, 'to_dict') and callable(instance.to_dict), \
            'to_dict must be callable method'
        serialized = instance.to_dict()
        assert type(serialized) is dict, 'to_dict must return dict'

    with TestCase('implementation.from_dict deserializes and returns instance'):
        instance = implementation(b'left', b'right')
        serialized = instance.to_dict()
        assert hasattr(implementation, 'from_dict'), 'implementation missing from_dict'
        deserialized = implementation.from_dict(serialized)
        assert type(deserialized) is implementation, \
            'from_dict must return instance of implementation'
        assert instance == deserialized, \
            'from_dict must return instance equal to source instance'

    with TestCase('implementation.from_dict raises errors for invalid params'):
        with RaisesError('from_dict must raise error on non-dict input') as e:
            implementation.from_dict('not a dict')
        eton(str(e.exception) == 'data must be dict type',
            f'{e.label}: incorrect error message')

        with RaisesError('from_dict must raise error on dict input with != 1 key') as e:
            implementation.from_dict({})
        eton(str(e.exception) == 'data must have one key',
            f'{e.label}: incorrect error message')

        with RaisesError('from_dict must raise error on dict input with != 1 key') as e:
            implementation.from_dict({**serialized, 'what': 'huh'})
        eton(str(e.exception) == 'data must have one key',
            f'{e.label}: incorrect error message')

        with RaisesError('from_dict must raise error on more than left and right branches') as e:
            implementation.from_dict({"3231": [1,2,3]})
        eton(str(e.exception) == 'data[root] must have left and right branch',
            f'{e.label}: incorrect error message')

        key = list(serialized.keys())[0]
        with RaisesError('from_dict must raise error on root mismatch') as e:
            implementation.from_dict({"3232": serialized[key]})
        eton(str(e.exception) == 'root mismatch',
            f'{e.label}: incorrect error message')

    with TestCase('instance.prove produces list of bytes proof'):
        for i in range(2, 300):
            leaves = [n.to_bytes(2, 'big') for n in range(i)]
            instance = implementation.from_leaves(leaves)
            proof = instance.prove(randint(0, i-1).to_bytes(2, 'big'))
            proof_verbose = instance.prove(randint(0, i-1).to_bytes(2, 'big'), verbose=True)
            assert type(proof) is list
            assert type(proof_verbose) is list
            for step in proof:
                assert type(step) is bytes
            for step in proof_verbose:
                assert type(step) is bytes

    with TestCase('prove raises errors for invalid params'):
        leaves = [n.to_bytes(2, 'big') for n in range(13)]
        instance = implementation.from_leaves(leaves)

        with RaisesError('instance.prove must raise error for non-bytes input') as e:
            instance.prove('not bytes')
        eton(str(e.exception) == 'leaf must be bytes',
            f'{e.label}: incorrect error message')

        with RaisesError('instance.prove must raise error for leaf not in tree') as e:
            instance.prove(b'not in tree')
        eton(str(e.exception) == 'the given leaf was not found in the tree',
            f'{e.label}: incorrect error message')

    with TestCase('verify executes without error for valid proof'):
        for i in range(2, 300):
            leaves = [n.to_bytes(2, 'big') for n in range(i)]
            instance = implementation.from_leaves(leaves)
            leaf = randint(0, i-1).to_bytes(2, 'big')
            proof = instance.prove(leaf)
            implementation.verify(instance.root, leaf, proof)

    with TestCase('verify raises erorrs for invalid params'):
        leaves = [n.to_bytes(2, 'big') for n in range(13)]
        tree = implementation.from_leaves(leaves)
        leaf = leaves[3]
        proof = tree.prove(leaf)

        with RaisesError('should error on non-bytes root') as e:
            implementation.verify('tree.root', leaf, proof)
        eton(str(e.exception) == 'root must be bytes',
            f'{e.label}: incorrect error message')

        with RaisesError('should error on non-bytes leaf') as e:
            implementation.verify(tree.root, 'leaf', proof)
        eton(str(e.exception) == 'leaf must be bytes',
            f'{e.label}: incorrect error message')

        with RaisesError('should error on non-list proof') as e:
            implementation.verify(tree.root, leaf, {'not': 'list'})
        eton(str(e.exception) == 'proof must be list of bytes',
            f'{e.label}: incorrect error message')

        with RaisesError('should error on proof with list of non-bytes'):
            wrong_proof = ['not bytes']
            implementation.verify(tree.root, leaf, wrong_proof)
        eton(str(e.exception) == 'proof must be list of bytes',
            f'{e.label}: incorrect error message')

    with TestCase('verify raises errors for invalid proofs'):
        leaves = [n.to_bytes(2, 'big') for n in range(13)]
        tree = implementation.from_leaves(leaves)
        leaf = leaves[3]
        proof = tree.prove(leaf)

        with RaisesError('should error when proof does not reference leaf') as e:
            implementation.verify(tree.root, leaf + b'1', proof)
        eton(str(e.exception) == 'proof does not reference leaf',
            f'{e.label}: incorrect error message')

        with RaisesError('should error when proof does not reference leaf') as e:
            wrong_proof = proof[1:]
            implementation.verify(tree.root, leaf, wrong_proof)
        eton(str(e.exception) == 'proof does not reference leaf',
            f'{e.label}: incorrect error message')

        with RaisesError('should error when proof missing final hash operation') as e:
            wrong_proof = proof[:-1]
            implementation.verify(tree.root, leaf, wrong_proof)
        eton(str(e.exception) == 'proof missing final_hash op',
            f'{e.label}: incorrect error message')

        with RaisesError('should error when proof does not reference root') as e:
            wrong_proof = [*proof]
            wrong_proof[-1] = wrong_proof[-1] + b'1'
            implementation.verify(tree.root, leaf, wrong_proof)
        eton(str(e.exception) == 'proof does not reference root',
            f'{e.label}: incorrect error message')

        with RaisesError('should error when proof final hash does not match') as e:
            wrong_proof = [*proof]
            wrong_proof[1] = wrong_proof[1] + b'\x99'
            implementation.verify(tree.root, leaf, wrong_proof)
        eton(str(e.exception) == 'final hash does not match',
            f'{e.label}: incorrect error message')

    with TestCase('e2e arbitrary branching'):
        leaves = [hashlib.sha256(n.to_bytes(2, 'big')).digest() for n in range(13)]

        instance = implementation(leaves[0], leaves[1])
        for i in range(2, len(leaves)):
            if randint(0, 1) == 0:
                instance = implementation(instance, leaves[i])
            else:
                instance = implementation(leaves[i], instance)

        leaf = leaves[randint(0, len(leaves)-1)]
        proof1 = instance.prove(leaf)
        proof2 = instance.prove(leaf, verbose=True)
        implementation.verify(instance.root, leaf, proof1)
        implementation.verify(instance.root, leaf, proof2)
